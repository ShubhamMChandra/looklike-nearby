import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { MainNav } from '@/components/layout/main-nav';
import { Toaster } from 'sonner';
import { AuthProvider } from '@/lib/auth';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'LookLike Nearby - B2B Referral Lead Generation',
  description: 'Find similar businesses nearby your best clients to unlock warm referral opportunities',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <div className="relative flex min-h-screen flex-col">
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
              <div className="container flex h-14 items-center">
                <MainNav />
              </div>
            </header>
            <main className="flex-1">
              <div className="container py-6">
                {children}
              </div>
            </main>
            <Toaster />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}