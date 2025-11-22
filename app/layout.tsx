import type { Metadata } from 'next'
import { SpeedInsights } from "@vercel/speed-insights/next"
import { Analytics } from "@vercel/analytics/next"
import RandomFavicon from '@/components/RandomFavicon'
import './globals.css'

export const metadata: Metadata = {
  title: 'Edgeworth Box',
  description: 'Interactive Edgeworth Box Visualization',
  icons: {
    icon: [
      { url: '/favicon-jones-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-jones-32x32.png', sizes: '32x32', type: 'image/png' },
      { url: '/favicon-jones.ico', sizes: 'any' },
    ],
    apple: [
      { url: '/apple-touch-icon-jones.png', sizes: '180x180', type: 'image/png' },
    ],
  },
  manifest: '/site-jones.webmanifest',
  openGraph: {
    title: 'Edgeworth Box',
    description: 'Interactive Edgeworth Box Visualization',
    type: 'website',
    images: [
      {
        url: '/apple-touch-icon-jones.png',
        width: 180,
        height: 180,
        alt: 'Edgeworth Box',
      },
    ],
  },
  twitter: {
    card: 'summary',
    title: 'Edgeworth Box',
    description: 'Interactive Edgeworth Box Visualization',
    images: ['/apple-touch-icon-jones.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        <RandomFavicon />
        {children}
        <SpeedInsights />
      </body>
    </html>
  )
}