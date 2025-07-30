import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [password, setPassword] = useState('')
  const [referenceClients, setReferenceClients] = useState([])
  const [searchResults, setSearchResults] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(false)

  // Authentication
  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        password: password
      })
      if (response.data.access_token) {
        localStorage.setItem('session_token', response.data.access_token)
        setIsAuthenticated(true)
        loadInitialData()
      }
    } catch (error) {
      alert('Invalid password')
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post(`${API_URL}/api/auth/logout`)
      localStorage.removeItem('session_token')
      setIsAuthenticated(false)
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  // Load initial data
  const loadInitialData = async () => {
    try {
      const token = localStorage.getItem('session_token')
      const headers = { Authorization: `Bearer ${token}` }
      
      const [clientsRes, campaignsRes] = await Promise.all([
        axios.get(`${API_URL}/api/reference-clients`, { headers }),
        axios.get(`${API_URL}/api/campaigns`, { headers })
      ])
      
      setReferenceClients(clientsRes.data.clients || [])
      setCampaigns(campaignsRes.data.campaigns || [])
    } catch (error) {
      console.error('Error loading data:', error)
    }
  }

  // Search prospects
  const handleSearch = async (formData) => {
    setLoading(true)
    try {
      const token = localStorage.getItem('session_token')
      const response = await axios.post(`${API_URL}/api/search/prospects`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSearchResults(response.data.results || [])
    } catch (error) {
      console.error('Search error:', error)
      alert('Search failed')
    } finally {
      setLoading(false)
    }
  }

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('session_token')
    if (token) {
      setIsAuthenticated(true)
      loadInitialData()
    }
  }, [])

  if (!isAuthenticated) {
    return (
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-4">
            <div className="card">
              <div className="card-header text-center">
                <h4><i className="fas fa-map-marker-alt me-2"></i>LookLike Nearby</h4>
              </div>
              <div className="card-body">
                <form onSubmit={handleLogin}>
                  <div className="mb-3">
                    <label className="form-label">Password</label>
                    <input
                      type="password"
                      className="form-control"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <button type="submit" className="btn btn-primary w-100">
                    Login
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Navigation */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container">
          <a className="navbar-brand" href="#">
            <i className="fas fa-map-marker-alt me-2"></i>
            LookLike Nearby
          </a>
          <div className="navbar-nav ms-auto">
            <button className="btn btn-link nav-link text-white" onClick={handleLogout}>
              <i className="fas fa-sign-out-alt me-1"></i>
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container-fluid mt-4">
        <div className="row">
          {/* Sidebar */}
          <div className="col-md-3">
            <SearchForm 
              referenceClients={referenceClients}
              onSearch={handleSearch}
              loading={loading}
            />
          </div>

          {/* Main Content */}
          <div className="col-md-9">
            <div className="card">
              <div className="card-header">
                <ul className="nav nav-tabs card-header-tabs">
                  <li className="nav-item">
                    <a className="nav-link active" href="#search">
                      <i className="fas fa-search me-2"></i>Search Results
                    </a>
                  </li>
                  <li className="nav-item">
                    <a className="nav-link" href="#campaigns">
                      <i className="fas fa-bullhorn me-2"></i>Campaigns ({campaigns.length})
                    </a>
                  </li>
                  <li className="nav-item">
                    <a className="nav-link" href="#clients">
                      <i className="fas fa-building me-2"></i>Reference Clients ({referenceClients.length})
                    </a>
                  </li>
                </ul>
              </div>
              <div className="card-body">
                <SearchResults results={searchResults} loading={loading} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Search Form Component
function SearchForm({ referenceClients, onSearch, loading }) {
  const [formData, setFormData] = useState({
    reference_client_id: '',
    business_name: '',
    address: '',
    business_type: '',
    radius_miles: 10,
    custom_address: '',
    custom_industry: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch(formData)
  }

  return (
    <div className="card">
      <div className="card-header">
        <h5><i className="fas fa-search me-2"></i>Quick Search</h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Reference Client</label>
            <select 
              className="form-select" 
              value={formData.reference_client_id}
              onChange={(e) => setFormData({...formData, reference_client_id: e.target.value})}
            >
              <option value="">Select existing client...</option>
              {referenceClients.map(client => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-3">
            <label className="form-label">Business Name</label>
            <input 
              type="text" 
              className="form-control" 
              value={formData.business_name}
              onChange={(e) => setFormData({...formData, business_name: e.target.value})}
              placeholder="Enter business name"
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Address</label>
            <input 
              type="text" 
              className="form-control" 
              value={formData.address}
              onChange={(e) => setFormData({...formData, address: e.target.value})}
              placeholder="Enter address"
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Search Radius</label>
            <select 
              className="form-select"
              value={formData.radius_miles}
              onChange={(e) => setFormData({...formData, radius_miles: parseInt(e.target.value)})}
            >
              <option value={5}>5 miles</option>
              <option value={10}>10 miles</option>
              <option value={25}>25 miles</option>
              <option value={50}>50 miles</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary w-100" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2"></span>
                Searching...
              </>
            ) : (
              <>
                <i className="fas fa-search me-2"></i>
                Search
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

// Search Results Component
function SearchResults({ results, loading }) {
  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Searching for similar businesses...</p>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-5 text-muted">
        <i className="fas fa-search fa-3x mb-3"></i>
        <h5>No search results yet</h5>
        <p>Use the search form to find similar businesses in your area.</p>
      </div>
    )
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5>Search Results ({results.length})</h5>
        <button className="btn btn-outline-primary btn-sm">
          <i className="fas fa-download me-1"></i>Export CSV
        </button>
      </div>
      
      <div className="row">
        {results.map((business, index) => (
          <div key={index} className="col-md-6 mb-3">
            <div className="card h-100">
              <div className="card-body">
                <h6 className="card-title">{business.name}</h6>
                <p className="card-text text-muted small">{business.address}</p>
                
                {business.rating && (
                  <div className="mb-2">
                    <span className="badge bg-warning text-dark">
                      <i className="fas fa-star"></i> {business.rating}
                    </span>
                  </div>
                )}
                
                <div className="d-flex gap-2">
                  <button className="btn btn-outline-primary btn-sm">
                    <i className="fas fa-plus me-1"></i>Add to Campaign
                  </button>
                  <button className="btn btn-outline-secondary btn-sm">
                    <i className="fas fa-eye me-1"></i>Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
