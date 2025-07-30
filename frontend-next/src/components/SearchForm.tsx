import { useState, useEffect } from 'react'
import api from '@/lib/api'

interface ReferenceClient {
  id: number
  business_name: string
  address: string
  business_type: string
}

interface SearchResult {
  name: string
  address: string
  types: string[]
  place_id: string
  distance: number
}

export default function SearchForm() {
  const [clients, setClients] = useState<ReferenceClient[]>([])
  const [selectedClient, setSelectedClient] = useState<string>('')
  const [radius, setRadius] = useState<number>(10)
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchClients()
  }, [])

  const fetchClients = async () => {
    try {
      const response = await api.get('/api/reference-clients')
      setClients(response.data)
    } catch (error) {
      console.error('Failed to fetch clients:', error)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedClient) return

    setLoading(true)
    try {
      const response = await api.post('/api/search', {
        reference_client_id: parseInt(selectedClient),
        radius_miles: radius
      })
      setResults(response.data.results)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSearch} className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Reference Client</label>
            <select
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            >
              <option value="">Select a client</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.business_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Search Radius (miles)</label>
            <select
              value={radius}
              onChange={(e) => setRadius(parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value={5}>5 miles</option>
              <option value={10}>10 miles</option>
              <option value={25}>25 miles</option>
              <option value={50}>50 miles</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
      </form>

      {results.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Search Results ({results.length})</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Business Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Distance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((result, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">{result.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{result.address}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{result.distance.toFixed(1)} mi</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button className="text-blue-600 hover:text-blue-900">
                        Add to Campaign
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}