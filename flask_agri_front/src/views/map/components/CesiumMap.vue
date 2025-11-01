<template>
  <div ref="cesiumContainer" class="cesium-bg"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElLoading } from 'element-plus'
import * as Cesium from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'

const { t } = useI18n()

const props = defineProps<{
  ionToken: string
  initialView?: { longitude: number; latitude: number; height: number }
  viewerOptions?: Partial<Cesium.Viewer.ConstructorOptions>
}>()

const cesiumContainer = ref<HTMLElement | null>(null)
let viewer: Cesium.Viewer | null = null
let routeEntities: Cesium.Entity[] = [] // 存储平面、标签、折线和无人机模型的实体

// 生成福州市上空的十个航线点
const generateRoutePoints = () => {
  const centerLon = 119.30 // 福州市中心经度
  const centerLat = 26.08 // 福州市中心纬度
  const height = 7000 // 高度 10,000 米
  const points = []

  // 生成十个点，随机偏移中心点
  for (let i = 0; i < 10; i++) {
    const lon = centerLon + (Math.random() - 0.5) * 0.05 // 经度偏移 ±0.025 度
    const lat = centerLat + (Math.random() - 0.5) * 0.05 // 纬度偏移 ±0.025 度
    // const h = height + ((Math.random() - 0.5)*1000)// 纬度偏移 ±0.025 度
    points.push({ longitude: lon, latitude: lat, height })
  }
  return points
}

onMounted(async () => {
  const loading = ElLoading.service({ text: t('loading') })
  try {
    if (!cesiumContainer.value) {
      throw new Error(t('error.containerNotFound'))
    }
    if (!props.ionToken) {
      throw new Error(t('error.ionTokenMissing'))
    }

    // 设置 Cesium Ion 访问令牌
    Cesium.Ion.defaultAccessToken = props.ionToken
    console.log('ionToken set:', props.ionToken)

    // 加载地形（间接验证 ionToken）
    let terrainProvider
    try {
      terrainProvider = await Cesium.createWorldTerrainAsync({
        ionAssetId: 1 // Cesium Ion 默认世界地形资源 ID
      })
    } catch (err) {
      throw new Error(t('error.ionTokenInvalid', { message: err.message }))
    }

    // 初始化 Viewer
    viewer = new Cesium.Viewer(cesiumContainer.value, {
      terrainProvider,
      animation: false,
      baseLayerPicker: false,
      fullscreenButton: false,
      geocoder: false,
      homeButton: false,
      infoBox: false,
      sceneModePicker: false,
      selectionIndicator: false,
      timeline: true, // 启用时间轴以支持动画
      navigationHelpButton: false,
      shouldAnimate: true,
      ...props.viewerOptions
    })

    // 配置地球光照和初始视角
    viewer.scene.globe.enableLighting = true
    viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(
        props.initialView?.longitude ?? 119.30, // 福州市经度
        props.initialView?.latitude ?? 26.08,  // 福州市纬度
        props.initialView?.height ?? 10000     // 高度 10,000 米
      )
    })

    // 添加航线点（圆形平面+序号标签）和折线
    const routePoints = generateRoutePoints()
    console.log('生成航线点:', routePoints)

    // 绘制圆形平面和序号标签
    routePoints.forEach((point, index) => {
      const entity = viewer.entities.add({
        name: `Route Point ${index + 1}`,
        position: Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, point.height),
        ellipse: {
          semiMinorAxis: 50.0, // 圆形半径（米）
          semiMajorAxis: 50.0, // 圆形半径（米）
          height: point.height, // 固定高度
          material: Cesium.Color.GREEN.withAlpha(0.5) // 半透明红色
        },
        label: {
          text: `${index + 1}`, // 序号（1, 2, ..., 10）
          font: '16px sans-serif',
          fillColor: Cesium.Color.WHITE,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 2,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: Cesium.VerticalOrigin.CENTER, // 标签居中
          pixelOffset: new Cesium.Cartesian2(0, 0) // 标签位于平面中央
        }
      })
      routeEntities.push(entity)
    })

    // 绘制折线（蓝色）
    const polylineEntity = viewer.entities.add({
      name: 'Route Polyline',
      polyline: {
        positions: Cesium.Cartesian3.fromDegreesArrayHeights(
          routePoints.flatMap(point => [point.longitude, point.latitude, point.height])
        ),
        width: 4,
        material: Cesium.Color.BLUE
      }
    })
    routeEntities.push(polylineEntity)

    // 创建无人机动画路径
    const startTime = Cesium.JulianDate.fromDate(new Date())
    const totalDuration = 50 // 总飞行时间（秒）
    const positionProperty = new Cesium.SampledPositionProperty()
    positionProperty.setInterpolationOptions({
      interpolationDegree: 1,
      interpolationAlgorithm: Cesium.LinearApproximation
    })

    // 为每个航线点设置时间戳
    routePoints.forEach((point, index) => {
      const time = Cesium.JulianDate.addSeconds(
        startTime,
        (index / (routePoints.length - 1)) * totalDuration,
        new Cesium.JulianDate()
      )
      const position = Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, point.height)
      positionProperty.addSample(time, position)
    })

    // 加载无人机模型并设置动画
    try {
      const droneEntity = viewer.entities.add({
        name: 'Drone Model',
        availability: new Cesium.TimeIntervalCollection([
          new Cesium.TimeInterval({
            start: startTime,
            stop: Cesium.JulianDate.addSeconds(startTime, totalDuration, new Cesium.JulianDate())
          })
        ]),
        position: positionProperty,
        orientation: new Cesium.VelocityOrientationProperty(positionProperty), // 自动根据路径调整朝向
        model: {
          uri: '/models/Drone.glb',
          scale: 100,
          minimumPixelSize: 64
        }
      })
      routeEntities.push(droneEntity)
      console.log('无人机模型加载成功:', '/models/Drone.glb')
    } catch (err) {
      console.error('无人机模型加载失败:', err)
      ElMessage.error(t('error.modelLoadFailed', { message: err.message || t('error.unknown') }))
    }

    // 配置时钟以支持循环动画
    viewer.clock.startTime = startTime.clone()
    viewer.clock.currentTime = startTime.clone()
    viewer.clock.stopTime = Cesium.JulianDate.addSeconds(startTime, totalDuration, new Cesium.JulianDate())
    viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP // 循环播放
    viewer.clock.multiplier = 1 // 正常速度
    viewer.clock.shouldAnimate = true

    console.log('航线点（圆形平面）、线和无人机模型添加成功:', routePoints.length, 'points')

    // 渲染错误监听
    viewer.scene.renderError.addEventListener((scene, error) => {
      console.error('Cesium 渲染错误:', error)
      ElMessage.error(t('error.renderError', { message: error.message }))
    })

    console.log('地形加载成功:', terrainProvider.ready)
  } catch (error) {
    console.error('Cesium 初始化失败:', error)
    ElMessage.error(t('error.initializationFailed', { message: error.message || t('error.unknown') }))
  } finally {
    loading.close()
  }
})

onUnmounted(() => {
  if (viewer) {
    console.log('销毁 Cesium Viewer 和航线实体')
    // 移除平面、标签、折线和无人机模型实体
    routeEntities.forEach(entity => viewer.entities.remove(entity))
    routeEntities = []
    viewer.destroy()
    viewer = null
  }
})
</script>

<style scoped lang="scss">
.cesium-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
}
</style>