import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/contexts/AuthContext'
import Layout from '@/components/Layout'
import DashboardNav from '@/components/DashboardNav'
import ReferenceClientList from '@/components/ReferenceClientList'
import SearchForm from '@/components/SearchForm'
import api from '@/lib/api'

export default function Dashboard() {
  const router = useRouter()
  const { isAuthenticated, logout } = useAuth()
  const [activeTab, setActiveTab] = useState('clients')
  const [stats, setStats] = useState({
    referenceClients: 0,
    campaigns: 0,
    prospects: 0,
    searches: 0
  })

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    } else {
      fetchStats()
    }
  }, [isAuthenticated, router])

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  return (
    <Layout title="Dashboard - LookLike Nearby">
      <div className="min-h-screen bg-gray-100">
        <DashboardNav onLogout={logout} />
        
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow px-6 py-4">
                <p className="text-sm text-gray-500">Reference Clients</p>
                <p className="text-2xl font-bold text-gray-900">{stats.referenceClients}</p>
              </div>
              <div className="bg-white rounded-lg shadow px-6 py-4">
                <p className="text-sm text-gray-500">Campaigns</p>
                <p className="text-2xl font-bold text-gray-900">{stats.campaigns}</p>
              </div>
              <div className="bg-white rounded-lg shadow px-6 py-4">
                <p className="text-sm text-gray-500">Prospects</p>
                <p className="text-2xl font-bold text-gray-900">{stats.prospects}</p>
              </div>
              <div className="bg-white rounded-lg shadow px-6 py-4">
                <p className="text-sm text-gray-500">Total Searches</p>
                <p className="text-2xl font-bold text-gray-900">{stats.searches}</p>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex">
                  <button
                    onClick={() => setActiveTab('clients')}
                    className={`py-2 px-4 border-b-2 font-medium text-sm ${
                      activeTab === 'clients'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Reference Clients
                  </button>
                  <button
                    onClick={() => setActiveTab('search')}
                    className={`ml-8 py-2 px-4 border-b-2 font-medium text-sm ${
                      activeTab === 'search'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Search Lookalikes
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {activeTab === 'clients' && <ReferenceClientList />}
                {activeTab === 'search' && <SearchForm />}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}