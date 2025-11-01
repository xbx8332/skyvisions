import log from 'loglevel'

// 设置默认日志级别
// 开发环境: DEBUG, 生产环境: ERROR
log.setLevel(import.meta.env.MODE === 'production' ? 'error' : 'debug')

// 可选：发送错误日志到后端
async function sendErrorToBackend(message: string, error: any) {
  try {
    // 假设后端 API 端点为 /api/log
    await fetch('/api/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        level: 'error',
        message,
        error: error instanceof Error ? { message: error.message, stack: error.stack } : error
      })
    })
  } catch (err) {
    console.warn('Failed to send error to backend:', err)
  }
}

// 包装日志方法，添加后端发送逻辑
const logger = {
  debug: (...args: any[]) => log.debug(...args),
  info: (...args: any[]) => log.info(...args),
  warn: (...args: any[]) => log.warn(...args),
  error: (message: string, error?: any) => {
    log.error(message, error)
    if (error && import.meta.env.MODE === 'production') {
      sendErrorToBackend(message, error)
    }
  }
}

export default logger