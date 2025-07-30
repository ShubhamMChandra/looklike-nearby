'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Toaster, toast } from 'sonner';
import { api } from '@/lib/api';
import { ReferenceClient } from '@/lib/types';

export default function ReferenceClientsPage() {
  const [clients, setClients] = useState<ReferenceClient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    business_type: '',
    notes: ''
  });

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const response = await api.getReferenceClients();
      if (response.data) {
        setClients(response.data);
      }
    } catch (error) {
      toast.error('Failed to load reference clients');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAdding(true);
    try {
      const response = await api.createReferenceClient(formData);
      if (response.data) {
        toast.success('Reference client added successfully!');
        setFormData({ name: '', address: '', business_type: '', notes: '' });
        loadClients();
      }
    } catch (error) {
      toast.error('Failed to add reference client');
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="space-y-6">
      <Toaster position="top-center" />
      
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Reference Clients</h1>
          <p className="text-muted-foreground">
            Manage your successful clients to use as reference points for finding similar businesses.
          </p>
        </div>
        <Button onClick={() => setIsAdding(true)}>Add Reference Client</Button>
      </div>

      {/* Add Client Form */}
      {isAdding && (
        <Card>
          <CardHeader>
            <CardTitle>Add Reference Client</CardTitle>
            <CardDescription>
              Add a successful client to use as a reference for finding similar businesses.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Business Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="business_type">Business Type</Label>
                  <Input
                    id="business_type"
                    value={formData.business_type}
                    onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
                    placeholder="e.g., Restaurant, Law Firm, etc."
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="address">Address *</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  required
                  placeholder="Full address including city and state"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Any additional notes about this client..."
                />
              </div>
              <div className="flex space-x-2">
                <Button type="submit" disabled={isAdding}>
                  {isAdding ? 'Adding...' : 'Add Client'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setIsAdding(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Clients List */}
      <div className="grid gap-4">
        {isLoading ? (
          <Card>
            <CardContent className="p-6">
              <p className="text-center text-muted-foreground">Loading reference clients...</p>
            </CardContent>
          </Card>
        ) : clients.length === 0 ? (
          <Card>
            <CardContent className="p-6">
              <p className="text-center text-muted-foreground">
                No reference clients yet. Add your first client to get started!
              </p>
            </CardContent>
          </Card>
        ) : (
          clients.map((client) => (
            <Card key={client.id}>
              <CardHeader>
                <CardTitle>{client.name}</CardTitle>
                <CardDescription>{client.address}</CardDescription>
              </CardHeader>
              <CardContent>
                {client.business_type && (
                  <p className="text-sm text-muted-foreground mb-2">
                    Type: {client.business_type}
                  </p>
                )}
                {client.notes && (
                  <p className="text-sm">{client.notes}</p>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
} 