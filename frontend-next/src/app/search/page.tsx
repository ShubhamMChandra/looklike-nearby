'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Toaster, toast } from 'sonner';
import { api } from '@/lib/api';
import { Prospect } from '@/lib/types';

export default function SearchPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [searchParams, setSearchParams] = useState({
    reference_client_id: undefined as number | undefined,
    radius_meters: 5000,
    custom_address: '',
    filters: {
      business_type: '',
      min_rating: undefined as number | undefined,
      max_price_level: undefined as number | undefined,
      open_now: undefined as boolean | undefined
    }
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await api.searchProspects(searchParams);
      if (response.data) {
        setProspects(response.data);
        toast.success(`Found ${response.data.length} prospects!`);
      }
    } catch {
      toast.error('Failed to search for prospects');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Toaster position="top-center" />
      
      <div>
        <h1 className="text-3xl font-bold">Search for Prospects</h1>
        <p className="text-muted-foreground">
          Find similar businesses near your reference clients or custom locations.
        </p>
      </div>

      {/* Search Form */}
      <Card>
        <CardHeader>
          <CardTitle>Search Parameters</CardTitle>
          <CardDescription>
            Configure your search to find the most relevant prospects.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="business_type">Business Type</Label>
                <Input
                  id="business_type"
                  value={searchParams.filters.business_type}
                  onChange={(e) => setSearchParams({ 
                    ...searchParams, 
                    filters: { ...searchParams.filters, business_type: e.target.value }
                  })}
                  placeholder="e.g., restaurant, law firm, etc."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="radius">Search Radius</Label>
                <Select
                  value={searchParams.radius_meters.toString()}
                  onValueChange={(value) => setSearchParams({ ...searchParams, radius_meters: parseInt(value) })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1000">1 km</SelectItem>
                    <SelectItem value="5000">5 km</SelectItem>
                    <SelectItem value="10000">10 km</SelectItem>
                    <SelectItem value="25000">25 km</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="custom_address">Custom Address (Optional)</Label>
              <Input
                id="custom_address"
                value={searchParams.custom_address}
                onChange={(e) => setSearchParams({ ...searchParams, custom_address: e.target.value })}
                placeholder="Enter a specific address to search from..."
              />
            </div>
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? 'Searching...' : 'Search for Prospects'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Results */}
      {prospects.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Search Results</h2>
          <div className="grid gap-4">
            {prospects.map((prospect) => (
              <Card key={prospect.id}>
                <CardHeader>
                  <CardTitle>{prospect.name}</CardTitle>
                  <CardDescription>{prospect.address}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {prospect.business_type && (
                      <div>
                        <span className="font-medium">Type:</span> {prospect.business_type}
                      </div>
                    )}
                    {prospect.phone && (
                      <div>
                        <span className="font-medium">Phone:</span> {prospect.phone}
                      </div>
                    )}
                    {prospect.website && (
                      <div>
                        <span className="font-medium">Website:</span> 
                        <a href={prospect.website} target="_blank" rel="noopener noreferrer" className="ml-1 text-blue-600 hover:underline">
                          Visit
                        </a>
                      </div>
                    )}
                    {prospect.rating && (
                      <div>
                        <span className="font-medium">Rating:</span> {prospect.rating}/5
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 