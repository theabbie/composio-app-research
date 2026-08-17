import { AgentSection } from './components/AgentSection'
import { AppsTable } from './components/AppsTable'
import { Footer } from './components/Footer'
import { Hero } from './components/Hero'
import { Nav } from './components/Nav'
import { Patterns } from './components/Patterns'
import { Verification } from './components/Verification'
import { analysis, apps } from './lib/data'

export default function App() {
  return (
    <div id="top" className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased">
      <Nav />
      <Hero analysis={analysis} />
      <Patterns analysis={analysis} />
      <AppsTable apps={apps} />
      <AgentSection analysis={analysis} />
      <Verification analysis={analysis} />
      <Footer />
    </div>
  )
}
