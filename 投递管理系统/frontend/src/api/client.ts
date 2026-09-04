import axios, { type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

/** axios 实例：baseURL 指向后端 /api/v1，由 vite 代理转发到 8000。 */
const client = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

client.interceptors.response.use(
  (resp: AxiosResponse<ApiResponse<unknown>>) => {
    const body = resp.data
    if (body && typeof body.code === 'number' && body.code !== 0) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message || 'error'))
    }
    return resp
  },
  (error) => {
    const msg =
      error.response?.data?.message || error.message || '网络错误，请检查后端服务'
    ElMessage.error(msg)
    return Promise.reject(error)
  },
)

/** 拆开统一信封，直接返回 data 字段。 */
async function unwrap<T>(p: Promise<AxiosResponse<ApiResponse<T>>>): Promise<T> {
  const r = await p
  return r.data.data as T
}

export { client, unwrap }
export default client
