'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { cn } from '@/lib/utils';
import { NavigationMenu, NavigationMenuItem, NavigationMenuLink, NavigationMenuList } from '@/components/ui/navigation-menu';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth';

export function MainNav() {
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();

  const routes = [
    {
      href: '/reference-clients',
      label: 'Reference Clients',
      active: pathname === '/reference-clients',
    },
    {
      href: '/search',
      label: 'Search',
      active: pathname === '/search',
    },
    {
      href: '/campaigns',
      label: 'Campaigns',
      active: pathname === '/campaigns',
    },
  ];

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex items-center space-x-4 lg:space-x-6">
      <NavigationMenu>
        <NavigationMenuList>
          {routes.map((route) => (
            <NavigationMenuItem key={route.href}>
              <Link href={route.href} legacyBehavior passHref>
                <NavigationMenuLink
                  className={cn(
                    'text-sm font-medium transition-colors hover:text-primary',
                    route.active ? 'text-black dark:text-white' : 'text-muted-foreground'
                  )}
                >
                  {route.label}
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
          ))}
        </NavigationMenuList>
      </NavigationMenu>
      <Button variant="ghost" onClick={logout}>
        Logout
      </Button>
    </div>
  );
}