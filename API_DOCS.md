# LookLike Nearby API Documentation

Base URL: `https://looklike-nearby-production.up.railway.app`

## Authentication

All endpoints except `/api/auth/login` require a Bearer token.

```typescript
// Example headers
const headers = {
  "Authorization": `Bearer ${token}`,
  "Content-Type": "application/json"
};
```

### Login
```typescript
// POST /api/auth/login
const response = await fetch(`${API_URL}/api/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ password: "airfare" })
});

const { access_token } = await response.json();
```

## Reference Clients

### List Reference Clients
```typescript
// GET /api/reference-clients
const response = await fetch(`${API_URL}/api/reference-clients`, {
  headers
});

const { clients, total } = await response.json();
// clients: Array<{
//   id: number;
//   name: string;
//   address: string;
//   business_type: string;
//   notes?: string;
//   latitude?: number;
//   longitude?: number;
// }>
```

### Create Reference Client
```typescript
// POST /api/reference-clients
const response = await fetch(`${API_URL}/api/reference-clients`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    name: "Test Restaurant",
    address: "123 Main St, Chicago, IL",
    business_type: "Restaurant",
    notes: "Great Italian food"
  })
});

const newClient = await response.json();
```

### Update Reference Client
```typescript
// PUT /api/reference-clients/{id}
const response = await fetch(`${API_URL}/api/reference-clients/1`, {
  method: "PUT",
  headers,
  body: JSON.stringify({
    name: "Updated Restaurant Name",
    address: "456 Oak St, Chicago, IL",
    business_type: "Restaurant",
    notes: "Updated notes"
  })
});

const updatedClient = await response.json();
```

### Delete Reference Client
```typescript
// DELETE /api/reference-clients/{id}
await fetch(`${API_URL}/api/reference-clients/1`, {
  method: "DELETE",
  headers
});
```

## Search

### Search for Prospects
```typescript
// GET /api/search
const params = new URLSearchParams({
  reference_client_id: "1",
  radius_meters: "5000",
  business_type: "Restaurant",
  min_rating: "4",
  max_price_level: "3",
  open_now: "true"
});

const response = await fetch(`${API_URL}/api/search?${params}`, {
  headers
});

const prospects = await response.json();
// prospects: Array<{
//   id: number;
//   name: string;
//   place_id: string;
//   address: string;
//   business_type: string;
//   rating?: number;
//   price_level?: number;
//   latitude: number;
//   longitude: number;
// }>
```

## V0 Component Examples

### Login Form
```typescript
// components/LoginForm.tsx
export default function LoginForm() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });

      if (!response.ok) {
        throw new Error("Invalid password");
      }

      const { access_token } = await response.json();
      localStorage.setItem("auth_token", access_token);
      // Redirect or update UI
    } catch (err) {
      setError("Login failed. Please try again.");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Enter password"
      />
      <button type="submit">Login</button>
      {error && <p className="text-red-500">{error}</p>}
    </form>
  );
}
```

### Reference Client List
```typescript
// components/ReferenceClientList.tsx
export default function ReferenceClientList() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        const response = await fetch(`${API_URL}/api/reference-clients`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch clients");
        }

        const { clients } = await response.json();
        setClients(clients);
      } catch (err) {
        console.error("Error fetching clients:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchClients();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="grid gap-4">
      {clients.map(client => (
        <div key={client.id} className="p-4 border rounded">
          <h3 className="font-bold">{client.name}</h3>
          <p>{client.address}</p>
          <p className="text-sm text-gray-600">{client.business_type}</p>
        </div>
      ))}
    </div>
  );
}
```

### Search Form
```typescript
// components/SearchForm.tsx
export default function SearchForm() {
  const [searchParams, setSearchParams] = useState({
    reference_client_id: "",
    radius_meters: "5000",
    business_type: "",
    min_rating: "",
    max_price_level: "",
    open_now: false
  });
  const [results, setResults] = useState([]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("auth_token");
      const params = new URLSearchParams();
      Object.entries(searchParams).forEach(([key, value]) => {
        if (value) params.append(key, value.toString());
      });

      const response = await fetch(`${API_URL}/api/search?${params}`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const prospects = await response.json();
      setResults(prospects);
    } catch (err) {
      console.error("Search error:", err);
    }
  };

  return (
    <form onSubmit={handleSearch}>
      <select
        value={searchParams.reference_client_id}
        onChange={(e) => setSearchParams({
          ...searchParams,
          reference_client_id: e.target.value
        })}
      >
        <option value="">Select Reference Client</option>
        {/* Add options from your clients list */}
      </select>

      <input
        type="text"
        value={searchParams.business_type}
        onChange={(e) => setSearchParams({
          ...searchParams,
          business_type: e.target.value
        })}
        placeholder="Business Type"
      />

      <input
        type="number"
        value={searchParams.radius_meters}
        onChange={(e) => setSearchParams({
          ...searchParams,
          radius_meters: e.target.value
        })}
        placeholder="Search Radius (meters)"
      />

      <button type="submit">Search</button>

      <div className="mt-4 grid gap-4">
        {results.map(prospect => (
          <div key={prospect.id} className="p-4 border rounded">
            <h3 className="font-bold">{prospect.name}</h3>
            <p>{prospect.address}</p>
            <p className="text-sm text-gray-600">
              Rating: {prospect.rating} | Price Level: {prospect.price_level}
            </p>
          </div>
        ))}
      </div>
    </form>
  );
}
```

## V0 Project Setup

1. Create a new V0 project
2. Add environment variables:
   ```env
   NEXT_PUBLIC_API_URL=https://looklike-nearby-production.up.railway.app
   ```

3. Create an API client utility:
   ```typescript
   // lib/api.ts
   const API_URL = process.env.NEXT_PUBLIC_API_URL;

   export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
     const token = localStorage.getItem("auth_token");
     const headers = {
       "Authorization": `Bearer ${token}`,
       "Content-Type": "application/json",
       ...options.headers
     };

     const response = await fetch(`${API_URL}${endpoint}`, {
       ...options,
       headers
     });

     if (!response.ok) {
       throw new Error("API request failed");
     }

     return response.json();
   }
   ```

4. Use the components above as starting points in V0's editor

## Error Handling

All endpoints return error responses in this format:
```typescript
{
  "detail": "Error message here"
}
```

Common error codes:
- 401: Unauthorized (missing or invalid token)
- 403: Forbidden (invalid password)
- 404: Not found
- 422: Validation error
- 500: Server error