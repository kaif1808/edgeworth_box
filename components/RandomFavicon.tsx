/**
 * Deprecated: RandomFavicon is no longer mounted.
 * Kept for reference in case dynamic favicon rotation is needed again.
 */
'use client'

import { useEffect } from 'react'

export default function RandomFavicon() {
  useEffect(() => {
    // Randomly select between 'jones' and 'daniel'
    const selected = Math.random() < 0.5 ? 'jones' : 'daniel'
    
    // Remove all existing favicon-related links first (in one pass)
    const allLinks = document.querySelectorAll('link[rel*="icon"], link[rel="manifest"], link[rel="shortcut icon"]')
    allLinks.forEach(link => {
      const linkHref = link.getAttribute('href')
      if (linkHref && (linkHref.includes('favicon') || linkHref.includes('apple-touch-icon') || linkHref.includes('manifest'))) {
        link.remove()
      }
    })
    
    // Helper function to create link element
    const createLink = (rel: string, href: string, sizes?: string, type?: string) => {
      const link = document.createElement('link')
      link.rel = rel
      link.href = href
      if (sizes) link.setAttribute('sizes', sizes)
      if (type) link.type = type
      document.head.appendChild(link)
    }
    
    // Add all favicon links (now safe since we removed all existing ones first)
    createLink('icon', `/favicon-${selected}-16x16.png`, '16x16', 'image/png')
    createLink('icon', `/favicon-${selected}-32x32.png`, '32x32', 'image/png')
    createLink('icon', `/favicon-${selected}.ico`, undefined, 'image/x-icon')
    
    // Add apple touch icon
    createLink('apple-touch-icon', `/apple-touch-icon-${selected}.png`, '180x180', 'image/png')
    
    // Add manifest
    createLink('manifest', `/site-${selected}.webmanifest`)
    
    // Add shortcut icon (for older browsers)
    createLink('shortcut icon', `/favicon-${selected}.ico`)
  }, [])
  
  return null
}

