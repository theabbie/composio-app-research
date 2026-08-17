const LINKS = [
  { href: '#patterns', label: 'Patterns' },
  { href: '#matrix', label: 'The 100 apps' },
  { href: '#agent', label: 'The agent' },
  { href: '#verification', label: 'Verification' },
  { href: '#run', label: 'Run it' },
]

export function Nav() {
  return (
    <nav className="sticky top-0 z-10 border-b border-zinc-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <a href="#top" className="font-mono text-sm font-semibold text-zinc-900">
          100-apps<span className="text-zinc-400">.research</span>
        </a>
        <div className="flex items-center gap-1">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-md px-2.5 py-1.5 text-xs font-medium text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  )
}
