import type { Metadata } from 'next'
import { Space_Grotesk, Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
})

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Shark Tank — AI Startup Interrogator',
  description: 'Pitch your startup idea to ruthless AI investors. Final project for AI Engineering, University of Oulu 2026.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable} h-full`}
    >
      <body className="h-full bg-background text-text antialiased" style={{ fontFamily: 'var(--font-body)' }}>
        {children}
        <footer
          className="fixed bottom-0 right-0 px-3 py-1.5 text-[10px] pointer-events-none"
          style={{ color: '#333', fontFamily: 'var(--font-mono)', zIndex: 9999 }}
        >
          AI Engineering · University of Oulu 2026 ·{' '}
          <a
            href="https://github.com/TheRealDarkCoder/AI-Engineering-2026"
            target="_blank"
            rel="noopener noreferrer"
            className="pointer-events-auto underline"
            style={{ color: '#444' }}
          >
            source
          </a>
        </footer>
      </body>
    </html>
  )
}
