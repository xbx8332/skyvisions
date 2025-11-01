import request from '@/api/request'

interface LoginResponse {
  access_token: string
  refresh_token: string
}

interface RefreshResponse {
  access_token: string
}

export const authApi = {
  login(username: string, password: string) {
    return request.post<LoginResponse>('/api/auth/login', { username, password })
  },
  logout() {
    return request.post('/api/auth/logout', {})
  },
  refresh(refreshToken: string) {
    return request.post<RefreshResponse>(
      '/api/auth/refresh',
      {},
      {
        headers: { Authorization: `Bearer ${refreshToken}` },
        skipError: true,
      }
    )
  },
}