
import request from '@/api/request'

interface Task {
  id: string
  description: string
  status: string
}

export const taskApi = {
  getTasks() {
    return request.get<Task[]>('/api/task')
  },
}