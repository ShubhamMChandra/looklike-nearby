import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '@/lib/api'

interface AuthContextType {
  isAuthenticated: boolean
  login: (password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token')
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        await api.get('/api/auth/verify')
        setIsAuthenticated(true)
      }
    } catch (error) {
      localStorage.removeItem('token')
      setIsAuthenticated(false)
    }
  }

  const login = async (password: string) => {
    const response = await api.post('/api/auth/login', { password })
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}