import Hero from "../components/Hero"
import PreviewCard from "../components/PreviewCard"
import Steps from "../components/Steps"

export default function HomePage() {
  return (
    <main className="home">
      <div className="hero-section">
        <Hero />
        <PreviewCard />
      </div>

      <Steps />
    </main>
  )
}
