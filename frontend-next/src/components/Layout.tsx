import { ReactNode } from 'react'
import Head from 'next/head'

interface LayoutProps {
  children: ReactNode
  title?: string
}

export default function Layout({ children, title = 'LookLike Nearby' }: LayoutProps) {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="B2B Referral Lead Generation Platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>{children}</main>
    </>
  )
}