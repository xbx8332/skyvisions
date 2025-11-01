import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import TWEEN from '@tweenjs/tween.js'

interface ThreeSceneOptions {
  particleCount?: number
  backgroundColor?: number
  backgroundAlpha?: number
  initialCameraZ?: number
  minZoom?: number
  maxZoom?: number
  zoomSpeed?: number
  rotationSpeed?: number
  particleSize?: number
  mapGeoJsonUrl?: string
  fujianGeoJsonUrl?: string
  mapScale?: number
}

export function useThreeScene(container: Ref<HTMLElement | null>, options: ThreeSceneOptions = {}) {
  const {
    particleCount = 5000,
    backgroundColor = 0x1a1a2e,
    backgroundAlpha = 0.5,
    initialCameraZ = 150,
    minZoom = 50,
    maxZoom = 500,
    zoomSpeed = 1.0,
    rotationSpeed = 1.0,
    particleSize = 2,
    mapGeoJsonUrl,
    fujianGeoJsonUrl = '/assets/json/fujian.json',
    mapScale = 1.0,
  } = options

  let scene: THREE.Scene
  let camera: THREE.PerspectiveCamera
  let renderer: THREE.WebGLRenderer
  let controls: OrbitControls
  let particles: THREE.Points
  let mapMesh: THREE.Group | null = null
  let fujianMesh: THREE.Group | null = null
  let pointLight1: THREE.PointLight
  let pointLight2: THREE.PointLight
  let composer: EffectComposer
  let raycaster: THREE.Raycaster
  let mouse: THREE.Vector2
  let lastIntersected: THREE.Mesh | null = null

  // 生成圆形纹理（用于粒子）
  const createCircleTexture = () => {
    const canvas = document.createElement('canvas')
    canvas.width = 32
    canvas.height = 32
    const context = canvas.getContext('2d')
    if (!context) return new THREE.Texture()

    context.beginPath()
    context.arc(16, 16, 16, 0, 2 * Math.PI)
    context.fillStyle = 'white'
    context.fill()

    const texture = new THREE.Texture(canvas)
    texture.needsUpdate = true
    return texture
  }

  // 回退：生成简化的中国地图轮廓纹理
  const createChinaMapTexture = () => {
    const canvas = document.createElement('canvas')
    canvas.width = 512
    canvas.height = 512
    const context = canvas.getContext('2d')
    if (!context) return new THREE.Texture()

    context.fillStyle = 'rgba(0, 0, 0, 0)'
    context.fillRect(0, 0, canvas.width, canvas.height)

    context.beginPath()
    context.moveTo(150, 100)
    context.lineTo(350, 100)
    context.lineTo(400, 300)
    context.lineTo(300, 400)
    context.lineTo(200, 350)
    context.lineTo(150, 200)
    context.closePath()

    context.fillStyle = 'rgba(128, 128, 128, 0.5)'
    context.fill()
    context.strokeStyle = '#ffffff'
    context.lineWidth = 4
    context.stroke()

    const texture = new THREE.Texture(canvas)
    texture.needsUpdate = true
    return texture
  }

  // 计算 GeoJSON 边界范围
  const calculateBounds = (geoJsonData: any) => {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
    try {
      geoJsonData.features.forEach((feature: any) => {
        const coords = feature.geometry.coordinates
        if (feature.geometry.type === 'Polygon') {
          coords[0].forEach(([x, y]: [number, number]) => {
            minX = Math.min(minX, x)
            maxX = Math.max(maxX, x)
            minY = Math.min(minY, y)
            maxY = Math.max(maxY, y)
          })
        } else if (feature.geometry.type === 'MultiPolygon') {
          coords.forEach((poly: any) => {
            poly[0].forEach(([x, y]: [number, number]) => {
              minX = Math.min(minX, x)
              maxX = Math.max(maxX, x)
              minY = Math.min(minY, y)
              maxY = Math.max(maxY, y)
            })
          })
        }
      })
    } catch (error) {
      console.error('计算边界失败:', error)
    }
    return { minX, maxX, minY, maxY }
  }

  // 计算单个 Feature 的边界框
  const calculateFeatureBounds = (feature: any) => {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
    try {
      const coords = feature.geometry.coordinates
      if (feature.geometry.type === 'Polygon') {
        coords[0].forEach(([x, y]: [number, number]) => {
          minX = Math.min(minX, x)
          maxX = Math.max(maxX, x)
          minY = Math.min(minY, y)
          maxY = Math.max(maxY, y)
        })
      } else if (feature.geometry.type === 'MultiPolygon') {
        coords.forEach((poly: any) => {
          poly[0].forEach(([x, y]: [number, number]) => {
            minX = Math.min(minX, x)
            maxX = Math.max(maxX, x)
            minY = Math.min(minY, y)
            maxY = Math.max(maxY, y)
          })
        })
      }
      return { minX, maxX, minY, maxY }
    } catch (error) {
      console.error(`计算 ${feature.properties?.name} 边界框失败:`, error)
      return null
    }
  }

  // 合并所有 Feature 为单一 MultiPolygon
  const mergeFeaturesToMultiPolygon = (geoJsonData: any) => {
    try {
      const coordinates = geoJsonData.features
        .filter((f: any) => ['Polygon', 'MultiPolygon'].includes(f.geometry.type))
        .flatMap((f: any) => {
          if (f.geometry.type === 'Polygon') {
            return [f.geometry.coordinates]
          } else {
            return f.geometry.coordinates
          }
        })
      return {
        type: 'Feature',
        geometry: {
          type: 'MultiPolygon',
          coordinates,
        },
        properties: { name: 'Merged' },
      }
    } catch (error) {
      console.error('合并 Feature 失败:', error)
      return null
    }
  }

  // 使用 THREE.Shape 绘制 MultiPolygon 并挤出
  const createShapeGeometry = (feature: any, scale: number, depth: number = 2) => {
    const shapes: THREE.Shape[] = []
    try {
      const coords = feature.geometry.type === 'Polygon'
        ? [feature.geometry.coordinates]
        : feature.geometry.coordinates

      coords.forEach((poly: any) => {
        const shape = new THREE.Shape()
        poly[0].forEach(([x, y]: [number, number], i: number) => {
          if (i === 0) shape.moveTo(x * scale, y * scale)
          else shape.lineTo(x * scale, y * scale)
        })
        shapes.push(shape)
      })

      const geometry = new THREE.ExtrudeGeometry(shapes, {
        depth,
        bevelEnabled: false,
        steps: 1,
      })
      return geometry
    } catch (error) {
      console.error('创建 ShapeGeometry 失败:', error)
      return null
    }
  }

  // 为单个 Feature 创建边界线（用于中国地图省级边界）
  const createFeatureOutline = (feature: any, scale: number, zOffset: number = 0.1) => {
    const shapes: THREE.Shape[] = []
    try {
      const coords = feature.geometry.type === 'Polygon'
        ? [feature.geometry.coordinates]
        : feature.geometry.coordinates

      coords.forEach((poly: any) => {
        const shape = new THREE.Shape()
        poly[0].forEach(([x, y]: [number, number], i: number) => {
          if (i === 0) shape.moveTo(x * scale, y * scale)
          else shape.lineTo(x * scale, y * scale)
        })
        shapes.push(shape)
      })

      const geometry = new THREE.ShapeGeometry(shapes)
      const edges = new THREE.EdgesGeometry(geometry)

      // 抬高边界线
      const positions = edges.attributes.position.array
      for (let i = 2; i < positions.length; i += 3) {
        positions[i] = zOffset
      }
      edges.attributes.position.needsUpdate = true

      const material = new THREE.ShaderMaterial({
        uniforms: {
          glowColor: { value: new THREE.Color(0x4adeff) }, // 浅科技蓝
          glowIntensity: { value: 3.0 },
          time: { value: 0.0 },
        },
        vertexShader: `
          varying vec3 vPosition;
          void main() {
            vPosition = position;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          uniform vec3 glowColor;
          uniform float glowIntensity;
          uniform float time;
          varying vec3 vPosition;
          void main() {
            float intensity = glowIntensity * (0.5 + 0.5 * sin(time * 5.0));
            gl_FragColor = vec4(glowColor, intensity);
          }
        `,
        transparent: true,
        side: THREE.DoubleSide,
        depthTest: false,
        depthWrite: false,
      })

      const line = new THREE.LineSegments(edges, material)
      line.name = feature.properties?.name || 'unnamed'
      line.renderOrder = 1
      console.log(`Feature ${feature.properties?.name} 边界线顶点数:`, edges.attributes.position?.count || 0)
      console.log(`边界线材质参数:`, {
        glowColor: material.uniforms.glowColor.value.getHexString(),
        glowIntensity: material.uniforms.glowIntensity.value,
        renderOrder: line.renderOrder,
      })
      return [line]
    } catch (error) {
      console.error(`创建边界线失败 (${feature.properties?.name}):`, error)
      return []
    }
  }

  // 为单个 Feature 创建立方体和边界线（用于福建省市级区域）
  const createFeatureCubes = (feature: any, scale: number, zOffset: number = 0) => {
    const objects: THREE.Object3D[] = []
    try {
      // 创建不规则多边形几何体
      const shapes: THREE.Shape[] = []
      const coords = feature.geometry.type === 'Polygon'
        ? [feature.geometry.coordinates]
        : feature.geometry.coordinates

      coords.forEach((poly: any, polyIndex: number) => {
        const shape = new THREE.Shape()
        poly[0].forEach(([x, y]: [number, number], i: number) => {
          if (i === 0) shape.moveTo(x * scale, y * scale)
          else shape.lineTo(x * scale, y * scale)
        })
        // 处理空洞
        if (poly.length > 1) {
          poly.slice(1).forEach((hole: any) => {
            const holeShape = new THREE.Path()
            hole.forEach(([x, y]: [number, number], i: number) => {
              if (i === 0) holeShape.moveTo(x * scale, y * scale)
              else holeShape.lineTo(x * scale, y * scale)
            })
            shape.holes.push(holeShape)
          })
        }
        shapes.push(shape)
      })

      // 使用 ExtrudeGeometry 创建薄立方体
      const initialDepth = 0.01
      const geometry = new THREE.ExtrudeGeometry(shapes, {
        depth: initialDepth,
        bevelEnabled: false,
        steps: 1,
      })
      console.log(`Feature ${feature.properties?.name} 立方体顶点数:`, geometry.attributes.position?.count || 0)

      // 科技感深蓝色材质（不透明）
      const cubeMaterial = new THREE.MeshBasicMaterial({
        color: 0x1e90ff, // 深蓝色
        transparent: false,
        opacity: 1.0,
        side: THREE.DoubleSide,
      })

      const cubeMesh = new THREE.Mesh(geometry, cubeMaterial)
      cubeMesh.name = feature.properties?.name ? `${feature.properties.name}_Cube` : 'unnamed_Cube'
      cubeMesh.position.set(0, 0, zOffset + initialDepth / 2) // 中心点调整
      cubeMesh.renderOrder = 1
      // 存储原始数据以便动态更新
      cubeMesh.userData = {
        shapes,
        initialDepth,
        currentDepth: initialDepth,
        scale,
        zOffset,
        isAnimating: false,
      }
      console.log(`立方体材质参数 (${cubeMesh.name}):`, {
        color: cubeMaterial.color.getHexString(),
        opacity: cubeMaterial.opacity,
        side: cubeMaterial.side === THREE.DoubleSide ? 'DoubleSide' : 'FrontSide',
        position: cubeMesh.position.toArray(),
      })
      objects.push(cubeMesh)

      // 创建市级边缘边界线（z = zOffset + 0.02）
      const edgeLineGeometry = new THREE.ShapeGeometry(shapes)
      const edgeEdges = new THREE.EdgesGeometry(edgeLineGeometry)

      // 抬高边缘边界线
      const edgeLinePositions = edgeEdges.attributes.position.array
      for (let i = 2; i < edgeLinePositions.length; i += 3) {
        edgeLinePositions[i] = zOffset + 0.02
      }
      edgeEdges.attributes.position.needsUpdate = true

      const edgeLineMaterial = new THREE.LineBasicMaterial({
        color: 0xcc8400, // 深橙色
        transparent: false,
        linewidth: 1,
      })

      const edgeLine = new THREE.LineSegments(edgeEdges, edgeLineMaterial)
      edgeLine.name = feature.properties?.name ? `${feature.properties.name}_EdgeOutline` : 'unnamed_EdgeOutline'
      edgeLine.renderOrder = 2
      console.log(`市级边缘边界线材质参数 (${edgeLine.name}):`, {
        color: edgeLineMaterial.color.getHexString(),
        linewidth: edgeLineMaterial.linewidth,
        renderOrder: edgeLine.renderOrder,
      })
      objects.push(edgeLine)

      // 创建市级上平面边界线（z = zOffset + initialDepth / 2）
      const topLineGeometry = new THREE.ShapeGeometry(shapes)
      const topEdges = new THREE.EdgesGeometry(topLineGeometry)

      // 设置上平面边界线与立方体顶部齐平
      const topLinePositions = topEdges.attributes.position.array
      for (let i = 2; i < topLinePositions.length; i += 3) {
        topLinePositions[i] = zOffset + initialDepth / 2
      }
      topEdges.attributes.position.needsUpdate = true

      const topLineMaterial = new THREE.LineBasicMaterial({
        color: 0xcc8400, // 深橙色
        transparent: false,
        linewidth: 1,
      })

      const topLine = new THREE.LineSegments(topEdges, topLineMaterial)
      topLine.name = feature.properties?.name ? `${feature.properties.name}_TopOutline` : 'unnamed_TopOutline'
      topLine.renderOrder = 2
      topLine.userData = { zOffset, initialDepth }
      console.log(`市级上平面边界线材质参数 (${topLine.name}):`, {
        color: topLineMaterial.color.getHexString(),
        linewidth: topLineMaterial.linewidth,
        renderOrder: topLine.renderOrder,
      })
      objects.push(topLine)

      return objects
    } catch (error) {
      console.error(`创建立方体或边界线失败 (${feature.properties?.name}):`, error)
      return []
    }
  }

  // 创建福建省市级立方体和边界线（无主体效果）
  const createFujianMap = async (chinaBounds: any, chinaScale: number) => {
    if (!fujianGeoJsonUrl) {
      console.warn('未提供福建省 GeoJSON URL，跳过福建省处理')
      return null
    }

    try {
      console.log('尝试加载福建省 GeoJSON:', fujianGeoJsonUrl)
      const response = await fetch(fujianGeoJsonUrl)
      if (!response.ok) {
        throw new Error(`HTTP 错误: ${response.status} ${response.statusText}`)
      }
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        console.error('响应内容:', text.substring(0, 100))
        throw new Error(`响应不是 JSON 格式: ${contentType}`)
      }
      const geoJsonData = await response.json()
      console.log('福建省 GeoJSON 数据:', JSON.stringify(geoJsonData, null, 2))

      // 检查市级 Feature
      if (!geoJsonData.features || !Array.isArray(geoJsonData.features)) {
        throw new Error('福建省 GeoJSON 数据缺少 features 数组')
      }
      geoJsonData.features.forEach((feature: any, index: number) => {
        console.log(`Fujian Feature ${index}:`, {
          geometryType: feature.geometry?.type,
          properties: feature.properties,
          coordinateCount: feature.geometry?.coordinates?.flat(2).length / 2 || 0,
        })
      })

      // 计算福建省边界
      const fujianBounds = calculateBounds(geoJsonData)
      console.log('福建省 GeoJSON 边界:', fujianBounds)
      if (!isFinite(fujianBounds.minX) || !isFinite(fujianBounds.maxX)) {
        throw new Error('福建省边界计算无效')
      }

      // 使用与全国地图相同的缩放比例
      const dynamicScale = chinaScale
      console.log('福建省缩放比例:', dynamicScale)

      // 创建市级立方体和边界线
      const group = new THREE.Group()
      geoJsonData.features.forEach((feature: any) => {
        const objects = createFeatureCubes(feature, dynamicScale, 0)
        objects.forEach((obj) => group.add(obj))
      })

      // 设置位置
      group.position.set(0, 0, 1.0)
      group.name = 'FujianGroup'

      console.log('福建省 Mesh 添加状态:', '仅市级立方体和边界线')
      console.log('福建省位置:', group.position.toArray())
      console.log('中国边界参考:', chinaBounds)
      console.log('福建省边界参考:', fujianBounds)
      return group
    } catch (error) {
      console.error('加载福建省 GeoJSON 失败:', error)
      return null
    }
  }

  // 加载并解析 GeoJSON 创建中国地图（排除福建省）
  const createChinaMap = async () => {
    if (!mapGeoJsonUrl) {
      console.warn('未提供 GeoJSON URL，使用 Canvas 回退')
      const mapGeometry = new THREE.PlaneGeometry(100, 60)
      const mapMaterial = new THREE.MeshBasicMaterial({
        map: createChinaMapTexture(),
        transparent: true,
        side: THREE.DoubleSide,
      })
      return new THREE.Mesh(mapGeometry, mapMaterial)
    }

    try {
      console.log('尝试加载 GeoJSON:', mapGeoJsonUrl)
      const response = await fetch(mapGeoJsonUrl)
      if (!response.ok) {
        throw new Error(`HTTP 错误: ${response.status} ${response.statusText}`)
      }
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        console.error('响应内容:', text.substring(0, 100))
        throw new Error(`响应不是 JSON 格式: ${contentType}`)
      }
      const geoJsonData = await response.json()
      console.log('中国 GeoJSON 数据:', JSON.stringify(geoJsonData, null, 2))

      // 检查 Feature 类型
      if (!geoJsonData.features || !Array.isArray(geoJsonData.features)) {
        throw new Error('中国 GeoJSON 数据缺少 features 数组')
      }
      geoJsonData.features.forEach((feature: any, index: number) => {
        console.log(`Feature ${index}:`, {
          geometryType: feature.geometry?.type,
          properties: feature.properties,
          coordinateCount: feature.geometry?.coordinates?.flat(2).length / 2 || 0,
        })
      })

      // 排除福建省
      const filteredFeatures = geoJsonData.features.filter(
        (f: any) => f.properties.name !== '福建省' && f.properties.name !== 'Fujian'
      )
      const filteredGeoJson = { ...geoJsonData, features: filteredFeatures }
      console.log('过滤后 GeoJSON（排除福建省）:', filteredGeoJson)

      // 合并为单一 MultiPolygon
      const mergedFeature = mergeFeaturesToMultiPolygon(filteredGeoJson)
      if (!mergedFeature) {
        throw new Error('中国 Feature 合并失败')
      }
      console.log('合并后的 Feature:', {
        geometryType: mergedFeature.geometry.type,
        coordinateCount: mergedFeature.geometry.coordinates?.flat(2).length / 2 || 0,
      })

      // 计算边界并动态调整缩放
      const bounds = calculateBounds(geoJsonData)
      console.log('中国 GeoJSON 边界:', bounds)
      if (!isFinite(bounds.minX) || !isFinite(bounds.maxX)) {
        throw new Error('中国边界计算无效')
      }
      const lonRange = bounds.maxX - bounds.minX
      const latRange = bounds.maxY - bounds.minY
      const dynamicScale = Math.min(100 / lonRange, 60 / latRange) * mapScale
      console.log('中国缩放比例:', dynamicScale)

      // 创建全国地图几何体
      const geometry = createShapeGeometry(mergedFeature, dynamicScale)
      if (!geometry) {
        throw new Error('中国 ExtrudeGeometry 生成失败')
      }
      console.log('中国 Extrude 几何体顶点数:', geometry.attributes.position?.count || 0)

      const material = new THREE.MeshPhysicalMaterial({
        color: 0x808080,
        transparent: true,
        opacity: 0.5,
        roughness: 0.05,
        metalness: 0.2,
        reflectivity: 0.95,
        clearcoat: 0.8,
        clearcoatRoughness: 0.05,
        side: THREE.DoubleSide,
        envMap: null,
        envMapIntensity: 0,
        depthWrite: false,
      })
      console.log('地图材质参数:', {
        color: material.color.getHexString(),
        opacity: material.opacity,
        roughness: material.roughness,
        metalness: material.metalness,
        reflectivity: material.reflectivity,
        clearcoat: material.clearcoat,
        clearcoatRoughness: material.clearcoatRoughness,
        envMapIntensity: material.envMapIntensity,
      })

      const mesh = new THREE.Mesh(geometry, material)
      mesh.name = 'ChinaMesh'
      mesh.renderOrder = 0

      // 创建省级边界线
      const group = new THREE.Group()
      group.add(mesh)

      filteredGeoJson.features.forEach((feature: any) => {
        const lines = createFeatureOutline(feature, dynamicScale, 0.1)
        lines.forEach((line) => group.add(line))
      })

      // 创建福建省
      fujianMesh = await createFujianMap(bounds, dynamicScale)
      if (fujianMesh) {
        group.add(fujianMesh)
        console.log('福建省 Mesh 添加状态:', '已添加到场景')
      } else {
        console.warn('福建省 Mesh 未生成')
      }

      // 居中地图
      const centerX = (bounds.maxX + bounds.minX) / 2 * dynamicScale
      const centerY = (bounds.maxY + bounds.minY) / 2 * dynamicScale
      group.position.set(-centerX, -centerY, 0)
      group.name = 'ChinaGroup'
      console.log('中国地图位置:', group.position.toArray())

      return group
    } catch (error) {
      console.error('加载中国 GeoJSON 失败:', error)
      console.warn('回退到 Canvas 地图')
      const mapGeometry = new THREE.PlaneGeometry(100, 60)
      const mapMaterial = new THREE.MeshBasicMaterial({
        map: createChinaMapTexture(),
        transparent: true,
        side: THREE.DoubleSide,
      })
      return new THREE.Mesh(mapGeometry, mapMaterial)
    }
  }

  // 初始化场景
  const initScene = async () => {
    if (!container.value) return

    scene = new THREE.Scene()
    scene.background = new THREE.Color(backgroundColor)
    if (scene.background) scene.background.alpha = backgroundAlpha
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setClearColor(backgroundColor, backgroundAlpha)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.clear(true, true, true)
    container.value.appendChild(renderer.domElement)

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
    camera.position.set(0, 0, 150)
    camera.lookAt(0, 0, 0)

    // 添加 OrbitControls
    controls = new OrbitControls(camera, renderer.domElement)
    controls.minDistance = minZoom
    controls.maxDistance = maxZoom
    controls.zoomSpeed = zoomSpeed
    controls.rotateSpeed = rotationSpeed
    controls.enablePan = true
    controls.enableDamping = true
    controls.dampingFactor = 0.05

    // 初始化 Raycaster 和鼠标
    raycaster = new THREE.Raycaster()
    mouse = new THREE.Vector2()

    // 添加灯光
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
    scene.add(ambientLight)

    pointLight1 = new THREE.PointLight(0xffffff, 2.5, 200)
    pointLight1.position.set(30, 30, 30)
    scene.add(pointLight1)
    console.log('点光源1参数:', {
      position: pointLight1.position.toArray(),
      intensity: pointLight1.intensity,
      distance: pointLight1.distance,
    })

    pointLight2 = new THREE.PointLight(0xffffff, 2.0, 200)
    pointLight2.position.set(-30, -30, 30)
    scene.add(pointLight2)
    console.log('点光源2参数:', {
      position: pointLight2.position.toArray(),
      intensity: pointLight2.intensity,
      distance: pointLight2.distance,
    })

    // 添加调试辅助
    const axesHelper = new THREE.AxesHelper(50)
    scene.add(axesHelper)
    const lightHelper1 = new THREE.PointLightHelper(pointLight1, 5)
    const lightHelper2 = new THREE.PointLightHelper(pointLight2, 5)
    scene.add(lightHelper1, lightHelper2)

    // 添加后处理
    const renderPass = new RenderPass(scene, camera)
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      1.8,
      0.8,
      0.02
    )
    composer = new EffectComposer(renderer)
    composer.addPass(renderPass)
    composer.addPass(bloomPass)
    console.log('后处理参数:', {
      bloomStrength: bloomPass.strength,
      bloomRadius: bloomPass.radius,
      bloomThreshold: bloomPass.threshold,
    })

    const positions = new Float32Array(particleCount * 3)
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 1000
      positions[i + 1] = (Math.random() - 0.5) * 1000
      positions[i + 2] = (Math.random() - 0.5) * 1000
    }

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))

    const material = new THREE.PointsMaterial({
      color: 0xffffff,
      size: particleSize,
      sizeAttenuation: true,
      map: createCircleTexture(),
      transparent: true,
      alphaTest: 0.5,
    })

    particles = new THREE.Points(geometry, material)
    scene.add(particles)

    mapMesh = await createChinaMap()
    if (mapMesh) {
      scene.add(mapMesh)
      console.log('中国 Mesh 添加状态:', '已添加到场景')
    } else {
      console.warn('中国 Mesh 未生成')
    }

    // 添加鼠标移动事件
    const onMouseMove = (event: MouseEvent) => {
      if (!fujianMesh) return

      // 计算鼠标位置（归一化设备坐标）
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1

      // 更新 Raycaster
      raycaster.setFromCamera(mouse, camera)

      // 获取所有立方体
      const cubes: THREE.Mesh[] = []
      fujianMesh.traverse((child) => {
        if (child instanceof THREE.Mesh && child.name.includes('_Cube')) {
          cubes.push(child)
        }
      })

      // 检查交点
      const intersects = raycaster.intersectObjects(cubes)
      const intersected = intersects.length > 0 ? intersects[0].object as THREE.Mesh : null

      if (intersected && intersected !== lastIntersected) {
        // 鼠标进入新立方体
        if (lastIntersected && !lastIntersected.userData.isAnimating) {
          // 恢复上一个立方体高度
          const lastCube = lastIntersected
          const lastTopLine = fujianMesh.children.find(
            (child) => child.name === lastCube.name.replace('_Cube', '_TopOutline')
          ) as THREE.LineSegments
          new TWEEN.Tween({ depth: lastCube.userData.currentDepth })
            .to({ depth: lastCube.userData.initialDepth }, 500)
            .easing(TWEEN.Easing.Quadratic.InOut)
            .onUpdate(({ depth }) => {
              lastCube.userData.isAnimating = true
              lastCube.userData.currentDepth = depth
              const newGeometry = new THREE.ExtrudeGeometry(lastCube.userData.shapes, {
                depth,
                bevelEnabled: false,
                steps: 1,
              })
              lastCube.geometry.dispose()
              lastCube.geometry = newGeometry
              lastCube.position.set(0, 0, lastCube.userData.zOffset + depth / 2)
              if (lastTopLine) {
                const topLinePositions = (lastTopLine.geometry as THREE.BufferGeometry).attributes.position.array
                for (let i = 2; i < topLinePositions.length; i += 3) {
                  topLinePositions[i] = lastCube.userData.zOffset + depth / 2
                }
                (lastTopLine.geometry as THREE.BufferGeometry).attributes.position.needsUpdate = true
              }
            })
            .onComplete(() => {
              lastCube.userData.isAnimating = false
            })
            .start()
        }

        // 升高当前立方体
        if (!intersected.userData.isAnimating) {
          new TWEEN.Tween({ depth: intersected.userData.currentDepth })
            .to({ depth: 0.5 }, 500)
            .easing(TWEEN.Easing.Quadratic.InOut)
            .onUpdate(({ depth }) => {
              intersected.userData.isAnimating = true
              intersected.userData.currentDepth = depth
              const newGeometry = new THREE.ExtrudeGeometry(intersected.userData.shapes, {
                depth,
                bevelEnabled: false,
                steps: 1,
              })
              intersected.geometry.dispose()
              intersected.geometry = newGeometry
              intersected.position.set(0, 0, intersected.userData.zOffset + depth / 2)
              const topLine = fujianMesh.children.find(
                (child) => child.name === intersected.name.replace('_Cube', '_TopOutline')
              ) as THREE.LineSegments
              if (topLine) {
                const topLinePositions = (topLine.geometry as THREE.BufferGeometry).attributes.position.array
                for (let i = 2; i < topLinePositions.length; i += 3) {
                  topLinePositions[i] = intersected.userData.zOffset + depth / 2
                }
                (topLine.geometry as THREE.BufferGeometry).attributes.position.needsUpdate = true
              }
            })
            .onComplete(() => {
              intersected.userData.isAnimating = false
            })
            .start()
        }

        lastIntersected = intersected
        console.log(`鼠标悬停在: ${intersected.name}`)
      } else if (!intersected && lastIntersected && !lastIntersected.userData.isAnimating) {
        // 鼠标移开，恢复高度
        const lastCube = lastIntersected
        const lastTopLine = fujianMesh.children.find(
          (child) => child.name === lastCube.name.replace('_Cube', '_TopOutline')
        ) as THREE.LineSegments
        new TWEEN.Tween({ depth: lastCube.userData.currentDepth })
          .to({ depth: lastCube.userData.initialDepth }, 500)
          .easing(TWEEN.Easing.Quadratic.InOut)
          .onUpdate(({ depth }) => {
            lastCube.userData.isAnimating = true
            lastCube.userData.currentDepth = depth
            const newGeometry = new THREE.ExtrudeGeometry(lastCube.userData.shapes, {
              depth,
              bevelEnabled: false,
              steps: 1,
            })
            lastCube.geometry.dispose()
            lastCube.geometry = newGeometry
            lastCube.position.set(0, 0, lastCube.userData.zOffset + depth / 2)
            if (lastTopLine) {
              const topLinePositions = (lastTopLine.geometry as THREE.BufferGeometry).attributes.position.array
              for (let i = 2; i < topLinePositions.length; i += 3) {
                topLinePositions[i] = lastCube.userData.zOffset + depth / 2
              }
              (lastTopLine.geometry as THREE.BufferGeometry).attributes.position.needsUpdate = true
            }
          })
          .onComplete(() => {
            lastCube.userData.isAnimating = false
            lastIntersected = null
          })
          .start()
        console.log(`鼠标离开: ${lastCube.name}`)
      }
    }

    container.value.addEventListener('mousemove', onMouseMove)
  }

  const onWindowResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
    composer.setSize(window.innerWidth, window.innerHeight)
  }

  const animate = () => {
    requestAnimationFrame(animate)
    particles.rotation.y += 0.0002
    // 动态移动点光源
    pointLight1.position.x = 30 * Math.sin(Date.now() * 0.001)
    pointLight1.position.y = 30 * Math.cos(Date.now() * 0.001)
    pointLight1.position.z = 30 + 5 * Math.sin(Date.now() * 0.002)
    pointLight2.position.x = -30 * Math.sin(Date.now() * 0.001)
    pointLight2.position.y = -30 * Math.cos(Date.now() * 0.001)
    pointLight2.position.z = 30 + 5 * Math.cos(Date.now() * 0.002)

    // 更新边界线动画（仅省级边界线）
    if (mapMesh) {
      mapMesh.traverse((child) => {
        if (
          child instanceof THREE.LineSegments &&
          child.material instanceof THREE.ShaderMaterial
        ) {
          child.material.uniforms.time.value = Date.now() * 0.002
          const intensity = child.material.uniforms.glowIntensity.value * (0.5 + 0.5 * Math.sin(Date.now() * 0.002 * 5.0))
          console.log(`辉光强度 (${child.name}): ${intensity}`)
        }
      })
    }

    // 更新 TWEEN 动画
    TWEEN.update()

    composer.render()
  }

  onMounted(async () => {
    await initScene()
    window.addEventListener('resize', onWindowResize)
    animate()
  })

  onUnmounted(() => {
    if (renderer) {
      renderer.dispose()
      if (container.value) {
        container.value.removeChild(renderer.domElement)
      }
    }
    window.removeEventListener('resize', onWindowResize)
    if (container.value) {
      container.value.removeEventListener('mousemove', onMouseMove)
    }
  })

  return {
    scene,
    camera,
    renderer,
    controls,
    particles,
    mapMesh,
    fujianMesh,
  }
}