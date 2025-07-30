'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Toaster } from 'sonner';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
      <Toaster position="top-center" />
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Welcome to LookLike Nearby</CardTitle>
          <CardDescription>
            Find similar businesses nearby your best clients to unlock warm referral opportunities.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Ready to discover new prospects? Start by managing your reference clients.
            </p>
          </div>
          <div className="flex flex-col space-y-2">
            <Link href="/reference-clients">
              <Button className="w-full">
                Manage Reference Clients
              </Button>
            </Link>
            <Link href="/search">
              <Button variant="outline" className="w-full">
                Search for Prospects
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}