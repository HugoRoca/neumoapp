import Navbar from './Navbar'

/**
 * Main Layout Component
 * Wraps pages with navigation bar
 */
const MainLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="w-full max-w-7xl mx-auto">
        {children}
      </main>
    </div>
  )
}

export default MainLayout

