import type { Metadata } from 'next'
import { SpeedInsights } from "@vercel/speed-insights/next"
import { Analytics } from "@vercel/analytics/next"
// import RandomFavicon from '@/components/RandomFavicon'
import './globals.css'

export const metadata: Metadata = {
  metadataBase: new URL('https://imedgeworthboxingit.app'),
  title: 'Edgeworth Box Simulator & Solver | Interactive Economics Simulation',
  description: 'Free online Edgeworth Box simulator and solver. Visualize Pareto efficiency, Contract Curves, and Walrasian Equilibrium in this interactive economics demonstrator.',
  keywords: 'edgeworth box, economics simulator, pareto efficiency, contract curve, walrasian equilibrium, economics solver, microeconomics simulation, demonstrator',
  alternates: {
    canonical: '/',
  },
  icons: {
    icon: [
      { url: '/favicon-edge-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-edge-32x32.png', sizes: '32x32', type: 'image/png' },
      { url: '/favicon-edge.ico', sizes: 'any' },
    ],
    apple: [
      { url: '/apple-touch-icon-edge.png', sizes: '180x180', type: 'image/png' },
    ],
  },
  manifest: '/site-edge.webmanifest',
  openGraph: {
    title: 'Edgeworth Box Simulator & Solver',
    description: 'Interactive Edgeworth Box visualization and economics solver. Analyze Pareto efficiency and general equilibrium.',
    type: 'website',
    url: 'https://imedgeworthboxingit.app',
    images: [
      {
        url: '/apple-touch-icon-edge.png',
        width: 180,
        height: 180,
        alt: 'Edgeworth Box Simulator',
      },
    ],
  },
  twitter: {
    card: 'summary',
    title: 'Edgeworth Box Simulator & Solver',
    description: 'Interactive Edgeworth Box visualization and economics solver.',
    images: ['/apple-touch-icon-edge.png'],
  },
  verification: {
    google: 'sYbTbe6tv1L9hwiVASVyUiVokjGaMdmocW7RlnK3NG0',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'Edgeworth Box Simulator & Solver',
    applicationCategory: 'EducationalApplication',
    operatingSystem: 'Any',
    description: 'Free online Edgeworth Box simulator and solver. Visualize Pareto efficiency, Contract Curves, and Walrasian Equilibrium in this interactive economics demonstrator.',
    url: 'https://imedgeworthboxingit.app',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
  };

  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        {/* <RandomFavicon /> */}
        {children}
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  )
}
