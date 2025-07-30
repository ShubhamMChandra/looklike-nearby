interface DashboardNavProps {
  onLogout: () => void
}

export default function DashboardNav({ onLogout }: DashboardNavProps) {
  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold">LookLike Nearby</h1>
          </div>
          <div className="flex items-center">
            <button
              onClick={onLogout}
              className="ml-4 px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}