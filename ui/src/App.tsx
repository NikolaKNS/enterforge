import { useState, useRef } from 'react'
import {
  Bot,
  Settings,
  Package,
  Users,
  TrendingUp,
  Compass,
  Send,
  Sparkles,
  Palette,
  Globe,
  Sun,
  Moon,
  ChevronDown,
  Clock,
  Folder,
  MapPin,
  Calendar,
  DollarSign,
  X,
  FileText,
  User,
  Plane,
  Hotel,
  Star,
  Wifi,
  Coffee,
  Waves,
  Utensils,
  Dumbbell,
  Car,
  Search as SearchIcon,
} from 'lucide-react'

type View = 'agent' | 'projects' | 'arrangements' | 'settings'

interface Project {
  id: string
  title: string
  destination: string
  startDate: string
  endDate: string
  budget: string
  status: 'draft' | 'confirmed' | 'completed'
  createdAt: string
  description: string
  clientName: string
  travelers: number
  notes: string
}

interface RoomType {
  name: string
  count: number
  price: string
  beds: string
}

interface HotelData {
  id: string
  name: string
  location: string
  rating: number
  reviews: number
  pricePerNight: string
  amenities: string[]
  imageGradient: string
  availableFrom: string
  availableTo: string
  totalRooms: number
  rooms: RoomType[]
}

export default function App() {
  const [activeView, setActiveView] = useState<View>('agent')
  const [darkMode, setDarkMode] = useState(false)
  const [aiSuggestions, setAiSuggestions] = useState(true)
  const [inputValue, setInputValue] = useState('')
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const [projects, setProjects] = useState<Project[]>([
    {
      id: '1',
      title: 'Paris Romance Getaway',
      destination: 'Paris, France',
      startDate: '2026-05-15',
      endDate: '2026-05-22',
      budget: '$3,500',
      status: 'confirmed',
      createdAt: '2 days ago',
      description: 'A romantic 7-day escape to the City of Light featuring Seine river cruise, Eiffel Tower dinner, and guided Louvre tour.',
      clientName: 'Sarah & Michael Johnson',
      travelers: 2,
      notes: 'Anniversary trip. Requested champagne welcome and late checkout.',
    },
    {
      id: '2',
      title: 'Tokyo Business Trip',
      destination: 'Tokyo, Japan',
      startDate: '2026-06-10',
      endDate: '2026-06-18',
      budget: '$5,200',
      status: 'draft',
      createdAt: '5 hours ago',
      description: 'Corporate travel package with business-class flights, Shibuya hotel, and interpreter services.',
      clientName: 'Acme Corp',
      travelers: 4,
      notes: 'Need meeting rooms and airport transfers. Vegetarian meals required.',
    },
  ])

  const hotels: HotelData[] = [
    {
      id: 'h1',
      name: 'Le Grand Hotel Paris',
      location: 'Paris, France',
      rating: 4.8,
      reviews: 1243,
      pricePerNight: '$280',
      amenities: ['WiFi', 'Pool', 'Restaurant', 'Spa'],
      imageGradient: 'from-rose-400 to-orange-300',
      availableFrom: '2026-05-01',
      availableTo: '2026-08-31',
      totalRooms: 120,
      rooms: [
        { name: 'Standard Room', count: 40, price: '$220', beds: '1 Queen' },
        { name: 'Deluxe Suite', count: 50, price: '$280', beds: '1 King + Sofa' },
        { name: 'Presidential Suite', count: 20, price: '$450', beds: '2 King' },
        { name: 'Family Room', count: 10, price: '$320', beds: '2 Queen' },
      ],
    },
    {
      id: 'h2',
      name: 'Shibuya Excel Hotel',
      location: 'Tokyo, Japan',
      rating: 4.6,
      reviews: 892,
      pricePerNight: '$195',
      amenities: ['WiFi', 'Gym', 'Restaurant', 'Parking'],
      imageGradient: 'from-blue-400 to-cyan-300',
      availableFrom: '2026-04-15',
      availableTo: '2026-12-31',
      totalRooms: 85,
      rooms: [
        { name: 'Single Room', count: 20, price: '$150', beds: '1 Single' },
        { name: 'Double Room', count: 35, price: '$195', beds: '1 Queen' },
        { name: 'Business Suite', count: 20, price: '$260', beds: '1 King + Desk' },
        { name: 'Premium Corner', count: 10, price: '$310', beds: '1 King' },
      ],
    },
    {
      id: 'h3',
      name: 'Barcelona Beach Resort',
      location: 'Barcelona, Spain',
      rating: 4.7,
      reviews: 2105,
      pricePerNight: '$220',
      amenities: ['WiFi', 'Pool', 'Restaurant', 'Spa', 'Gym'],
      imageGradient: 'from-amber-400 to-yellow-300',
      availableFrom: '2026-03-01',
      availableTo: '2026-10-15',
      totalRooms: 200,
      rooms: [
        { name: 'Sea View Room', count: 80, price: '$220', beds: '1 King or 2 Twin' },
        { name: 'Pool Villa', count: 50, price: '$340', beds: '1 King + Daybed' },
        { name: 'Beachfront Suite', count: 40, price: '$420', beds: '1 King' },
        { name: 'Penthouse', count: 30, price: '$650', beds: '2 King' },
      ],
    },
    {
      id: 'h4',
      name: 'Bali Sunset Villas',
      location: 'Ubud, Bali',
      rating: 4.9,
      reviews: 567,
      pricePerNight: '$340',
      amenities: ['WiFi', 'Pool', 'Restaurant', 'Spa'],
      imageGradient: 'from-emerald-400 to-teal-300',
      availableFrom: '2026-01-01',
      availableTo: '2026-12-31',
      totalRooms: 45,
      rooms: [
        { name: 'Garden Villa', count: 20, price: '$340', beds: '1 King' },
        { name: 'Pool Villa', count: 15, price: '$480', beds: '1 King + Daybed' },
        { name: 'Riverside Suite', count: 8, price: '$620', beds: '1 King + 2 Single' },
        { name: 'Royal Pavilion', count: 2, price: '$1,200', beds: '2 King' },
      ],
    },
    {
      id: 'h5',
      name: 'New York Grand Central',
      location: 'New York, USA',
      rating: 4.5,
      reviews: 3421,
      pricePerNight: '$420',
      amenities: ['WiFi', 'Gym', 'Restaurant', 'Parking'],
      imageGradient: 'from-gray-400 to-slate-300',
      availableFrom: '2026-04-01',
      availableTo: '2026-11-30',
      totalRooms: 300,
      rooms: [
        { name: 'City Room', count: 100, price: '$420', beds: '1 Queen' },
        { name: 'Executive Suite', count: 80, price: '$580', beds: '1 King + Office' },
        { name: 'Skyline View', count: 70, price: '$650', beds: '1 King' },
        { name: 'Penthouse Loft', count: 50, price: '$950', beds: '2 King' },
      ],
    },
    {
      id: 'h6',
      name: 'Santorini Blue Suites',
      location: 'Santorini, Greece',
      rating: 4.9,
      reviews: 890,
      pricePerNight: '$380',
      amenities: ['WiFi', 'Pool', 'Restaurant', 'Spa'],
      imageGradient: 'from-sky-400 to-blue-300',
      availableFrom: '2026-04-01',
      availableTo: '2026-10-31',
      totalRooms: 60,
      rooms: [
        { name: 'Caldera Room', count: 25, price: '$380', beds: '1 Queen' },
        { name: 'Blue Dome Suite', count: 20, price: '$520', beds: '1 King + Jacuzzi' },
        { name: 'Infinity Villa', count: 12, price: '$780', beds: '1 King + 2 Single' },
        { name: 'Presidential Cliff', count: 3, price: '$1,500', beds: '2 King' },
      ],
    },
    {
      id: 'h7',
      name: 'Dubai Marina Tower',
      location: 'Dubai, UAE',
      rating: 4.7,
      reviews: 1567,
      pricePerNight: '$310',
      amenities: ['WiFi', 'Pool', 'Gym', 'Restaurant', 'Parking'],
      imageGradient: 'from-amber-500 to-orange-400',
      availableFrom: '2026-01-01',
      availableTo: '2026-12-31',
      totalRooms: 250,
      rooms: [
        { name: 'Marina Room', count: 80, price: '$310', beds: '1 King' },
        { name: 'Sky Suite', count: 70, price: '$450', beds: '1 King + Lounge' },
        { name: 'Executive Floor', count: 60, price: '$580', beds: '1 King + Office' },
        { name: 'Royal Penthouse', count: 40, price: '$1,100', beds: '2 King' },
      ],
    },
    {
      id: 'h8',
      name: 'London Thames House',
      location: 'London, UK',
      rating: 4.4,
      reviews: 2789,
      pricePerNight: '$265',
      amenities: ['WiFi', 'Restaurant', 'Gym'],
      imageGradient: 'from-red-400 to-rose-300',
      availableFrom: '2026-03-15',
      availableTo: '2026-09-30',
      totalRooms: 150,
      rooms: [
        { name: 'Thames Room', count: 60, price: '$265', beds: '1 Queen' },
        { name: 'Heritage Suite', count: 45, price: '$380', beds: '1 King + Sofa' },
        { name: 'Riverside View', count: 30, price: '$450', beds: '1 King' },
        { name: 'Royal Chamber', count: 15, price: '$720', beds: '2 King' },
      ],
    },
  ]

  const navItems: { key: View; label: string; icon: React.ElementType }[] = [
    { key: 'agent', label: 'AI Agent', icon: Bot },
    { key: 'projects', label: 'Projects', icon: Folder },
    { key: 'arrangements', label: 'Arrangements', icon: Hotel },
    { key: 'settings', label: 'Settings', icon: Settings },
  ]

  const addProject = () => {
    const destinations = [
      { city: 'Barcelona, Spain', title: 'Mediterranean Escape', desc: 'Beachfront resort with tapas tour and Gaudi architecture walk.', client: 'The Martinez Family', travelers: 3, notes: 'Kids-friendly activities requested.' },
      { city: 'Bali, Indonesia', title: 'Tropical Paradise Retreat', desc: 'Private villa with infinity pool, spa package, and temple visits.', client: 'Emma Wilson', travelers: 2, notes: 'Honeymoon. Requested flower bath and candlelight dinner.' },
      { city: 'New York, USA', title: 'City Adventure Package', desc: 'Broadway show tickets, Central Park bike tour, and rooftop dining.', client: 'James & Friends', travelers: 5, notes: 'Need adjacent hotel rooms. Broadway on Saturday night.' },
      { city: 'Santorini, Greece', title: 'Aegean Blue Dreams', desc: 'Cliffside suite with caldera views, wine tasting, and sunset cruise.', client: 'Robert & Linda Chen', travelers: 2, notes: 'Photography tour requested. Gluten-free dining.' },
      { city: 'Dubai, UAE', title: 'Luxury Desert Experience', desc: 'Burj Khalifa visit, desert safari, and Michelin-star dining.', client: 'Global Ventures Ltd', travelers: 6, notes: 'Business + leisure. Need conference room access.' },
    ]
    const dest = destinations[Math.floor(Math.random() * destinations.length)]
    const newProject: Project = {
      id: Date.now().toString(),
      title: dest.title,
      destination: dest.city,
      startDate: '2026-07-01',
      endDate: '2026-07-08',
      budget: '$' + (Math.floor(Math.random() * 5000) + 2000).toLocaleString(),
      status: 'draft',
      createdAt: 'Just now',
      description: dest.desc,
      clientName: dest.client,
      travelers: dest.travelers,
      notes: dest.notes,
    }
    setProjects((prev) => [newProject, ...prev])
  }

  const handleEditProject = (project: Project) => {
    setSelectedProject(project)
    setActiveView('agent')
  }

  const handleCloseProject = () => {
    setSelectedProject(null)
  }

  return (
    <div className={`flex h-screen w-full ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen w-full bg-gray-50 dark:bg-gray-950">
        {/* Sidebar */}
        <aside className="w-64 bg-sidebar text-sidebar-text flex flex-col flex-shrink-0">
          <div className="px-6 pt-6 pb-4">
            <h1 className="text-xl font-semibold text-white">TravelForge</h1>
            <p className="text-sm text-sidebar-muted mt-0.5">Enterprise edition</p>
          </div>

          <nav className="px-4 mt-2 flex-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeView === item.key
              return (
                <button
                  key={item.key}
                  onClick={() => setActiveView(item.key)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors mb-1 ${
                    isActive
                      ? 'bg-nav-active text-sidebar-text'
                      : 'text-sidebar-muted hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </button>
              )
            })}
          </nav>

          <div className="px-4 pb-6 mt-auto">
            <div className="flex items-center gap-3 px-2 py-3">
              <div className="w-9 h-9 rounded-full bg-nav-active flex items-center justify-center text-sidebar-text font-semibold text-sm">
                JD
              </div>
              <div>
                <p className="text-sm font-medium text-white">John Doe</p>
                <p className="text-xs text-sidebar-muted">Travel Agent</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {activeView === 'agent' ? (
            <AgentView
              inputValue={inputValue}
              setInputValue={setInputValue}
              onCreateArrangement={addProject}
              selectedProject={selectedProject}
              onCloseProject={handleCloseProject}
              inputRef={inputRef}
            />
          ) : activeView === 'projects' ? (
            <ProjectsView
              projects={projects}
              onEdit={handleEditProject}
            />
          ) : activeView === 'arrangements' ? (
            <ArrangementsView hotels={hotels} />
          ) : (
            <SettingsView
              darkMode={darkMode}
              setDarkMode={setDarkMode}
              aiSuggestions={aiSuggestions}
              setAiSuggestions={setAiSuggestions}
            />
          )}
        </main>
      </div>
    </div>
  )
}

function AgentView({
  inputValue,
  setInputValue,
  onCreateArrangement,
  selectedProject,
  onCloseProject,
  inputRef,
}: {
  inputValue: string
  setInputValue: (v: string) => void
  onCreateArrangement: () => void
  selectedProject: Project | null
  onCloseProject: () => void
  inputRef: React.RefObject<HTMLInputElement | null>
}) {
  const actions = [
    { icon: Package, label: 'Create a new arrangement', onClick: onCreateArrangement },
    { icon: Users, label: 'Find customer bookings' },
    { icon: TrendingUp, label: 'Analyze sales trends' },
    { icon: Compass, label: 'Suggest destinations' },
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Active Project Banner */}
      {selectedProject && (
        <div className="px-8 pt-6 pb-0">
          <div className="bg-accent-bg border border-accent/20 rounded-xl p-4 flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center flex-shrink-0">
                <Plane size={16} className="text-accent" />
              </div>
              <div>
                <p className="text-sm font-medium text-accent">Editing project: {selectedProject.title}</p>
                <p className="text-xs text-gray-600 dark:text-gray-300 mt-0.5">
                  {selectedProject.destination} · {selectedProject.startDate} → {selectedProject.endDate} · {selectedProject.budget}
                </p>
              </div>
            </div>
            <button
              onClick={onCloseProject}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors p-1"
            >
              <X size={18} />
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="px-8 pt-8 pb-6">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">AI Agent Assistant</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Your intelligent travel agency assistant</p>
      </div>

      {/* Action Cards */}
      <div className="px-8 grid grid-cols-4 gap-4">
        {actions.map((action, idx) => {
          const Icon = action.icon
          return (
            <button
              key={idx}
              onClick={action.onClick}
              className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 flex flex-col items-center gap-3 hover:shadow-sm dark:hover:shadow-gray-900/50 transition-shadow cursor-pointer text-center"
            >
              <div className="w-10 h-10 rounded-lg bg-accent-bg flex items-center justify-center text-accent">
                <Icon size={20} />
              </div>
              <span className="text-sm text-gray-900 dark:text-gray-100 font-medium">{action.label}</span>
            </button>
          )
        })}
      </div>

      {/* Chat Area */}
      <div className="flex-1 px-8 py-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl h-full flex flex-col">
          <div className="flex-1 p-6">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-5 max-w-3xl">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={16} className="text-accent" />
                <span className="text-sm font-medium text-accent">AI Assistant</span>
              </div>
              <p className="text-gray-800 dark:text-gray-200 text-sm leading-relaxed">
                Hello! I&apos;m your AI travel assistant. I can help you create arrangements, manage customer bookings,
                analyze trends, and answer questions about your travel agency operations. How can I assist you today?
              </p>
              <div className="flex items-center gap-1.5 mt-3 text-gray-500 dark:text-gray-400">
                <Clock size={13} />
                <span className="text-xs">Just now</span>
              </div>
            </div>
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-800">
            <div className="flex gap-3">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={
                  selectedProject
                    ? `Editing "${selectedProject.title}" — ask the AI to modify this arrangement...`
                    : "Ask me anything about your travel agency..."
                }
                className="flex-1 px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/50"
              />
              <button className="bg-accent hover:bg-accent/90 text-white px-5 py-3 rounded-lg flex items-center gap-2 transition-colors font-medium">
                <Send size={16} />
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ProjectsView({
  projects,
  onEdit,
}: {
  projects: Project[]
  onEdit: (project: Project) => void
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const statusColors: Record<string, string> = {
    draft: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    confirmed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    completed: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-8 pt-8 pb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Projects</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Arrangements created by the AI Agent</p>
        </div>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {projects.length} arrangement{projects.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="px-8 pb-8">
        {projects.length === 0 ? (
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-12 text-center">
            <Package size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">No arrangements yet</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Use the AI Agent to create your first travel arrangement.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {projects.map((project) => {
              const isExpanded = expandedId === project.id
              return (
                <div
                  key={project.id}
                  className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 hover:shadow-sm dark:hover:shadow-gray-900/50 transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">{project.title}</h3>
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                        statusColors[project.status] || 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                    </span>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-3 text-sm">
                      <MapPin size={16} className="text-gray-400 flex-shrink-0" />
                      <span className="text-gray-700 dark:text-gray-300">{project.destination}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm">
                      <Calendar size={16} className="text-gray-400 flex-shrink-0" />
                      <span className="text-gray-700 dark:text-gray-300">
                        {project.startDate} → {project.endDate}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-sm">
                      <DollarSign size={16} className="text-gray-400 flex-shrink-0" />
                      <span className="text-gray-700 dark:text-gray-300">{project.budget}</span>
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 space-y-3">
                      <div className="flex items-start gap-3 text-sm">
                        <FileText size={16} className="text-gray-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Description</p>
                          <p className="text-gray-700 dark:text-gray-300">{project.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-sm">
                        <User size={16} className="text-gray-400 flex-shrink-0" />
                        <div>
                          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-0.5">Client</p>
                          <p className="text-gray-700 dark:text-gray-300">{project.clientName} · {project.travelers} traveler{project.travelers !== 1 ? 's' : ''}</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3 text-sm">
                        <FileText size={16} className="text-gray-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Notes</p>
                          <p className="text-gray-700 dark:text-gray-300">{project.notes}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : project.id)}
                      className="text-sm text-accent hover:text-accent/80 font-medium transition-colors"
                    >
                      {isExpanded ? 'Hide details' : 'View details'}
                    </button>
                    <button
                      onClick={() => onEdit(project)}
                      className="text-sm text-gray-900 dark:text-gray-100 hover:text-accent dark:hover:text-accent font-medium transition-colors px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-accent dark:hover:border-accent"
                    >
                      Edit
                    </button>
                  </div>

                  <div className="mt-2 text-right">
                    <span className="text-xs text-gray-400 dark:text-gray-500">Created {project.createdAt}</span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function ArrangementsView({ hotels }: { hotels: HotelData[] }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [showSearch, setShowSearch] = useState(false)

  const filtered = hotels.filter(
    (h) =>
      h.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      h.location.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const amenityIcons: Record<string, React.ElementType> = {
    WiFi: Wifi,
    Pool: Waves,
    Restaurant: Utensils,
    Spa: Sparkles,
    Gym: Dumbbell,
    Parking: Car,
    Breakfast: Coffee,
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-8 pt-8 pb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Arrangements</h2>
            <p className="text-gray-500 dark:text-gray-400 mt-1">Hotels and accommodations in our network</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSearch(!showSearch)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                showSearch
                  ? 'bg-accent text-white'
                  : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:border-accent dark:hover:border-accent'
              }`}
            >
              <SearchIcon size={16} />
              Search
            </button>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {filtered.length} hotel{filtered.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>

        {/* Search Bar — toggled by Search button */}
        {showSearch && (
          <div className="mt-4 relative max-w-md">
            <SearchIcon size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search hotels by name or location..."
              autoFocus
              className="w-full pl-10 pr-10 py-2.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/50"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X size={14} />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Hotels Grid */}
      <div className="px-8 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((hotel) => {
            const isExpanded = expandedId === hotel.id
            return (
              <div
                key={hotel.id}
                className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden hover:shadow-sm dark:hover:shadow-gray-900/50 transition-shadow"
              >
                {/* Image placeholder */}
                <div className={`h-32 bg-gradient-to-br ${hotel.imageGradient} flex items-center justify-center`}>
                  <Hotel size={32} className="text-white/80" />
                </div>

                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 leading-tight">{hotel.name}</h3>
                  </div>

                  <div className="flex items-center gap-1.5 mb-3">
                    <MapPin size={13} className="text-gray-400" />
                    <span className="text-xs text-gray-500 dark:text-gray-400">{hotel.location}</span>
                  </div>

                  <div className="flex items-center gap-2 mb-3">
                    <div className="flex items-center gap-1">
                      <Star size={14} className="text-amber-400 fill-amber-400" />
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{hotel.rating}</span>
                    </div>
                    <span className="text-xs text-gray-400 dark:text-gray-500">({hotel.reviews.toLocaleString()} reviews)</span>
                  </div>

                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {hotel.amenities.map((amenity) => {
                      const Icon = amenityIcons[amenity] || Sparkles
                      return (
                        <span
                          key={amenity}
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-gray-100 dark:bg-gray-800 text-xs text-gray-600 dark:text-gray-300"
                        >
                          <Icon size={10} />
                          {amenity}
                        </span>
                      )
                    })}
                  </div>

                  {/* Expanded room details */}
                  {isExpanded && (
                    <div className="mb-4 pt-4 border-t border-gray-100 dark:border-gray-800 space-y-4">
                      {/* Availability */}
                      <div className="flex items-center gap-3 text-sm">
                        <Calendar size={16} className="text-gray-400 flex-shrink-0" />
                        <div>
                          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-0.5">Availability</p>
                          <p className="text-gray-700 dark:text-gray-300">{hotel.availableFrom} → {hotel.availableTo}</p>
                        </div>
                      </div>

                      {/* Total rooms */}
                      <div className="flex items-center gap-3 text-sm">
                        <Hotel size={16} className="text-gray-400 flex-shrink-0" />
                        <div>
                          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-0.5">Total Rooms</p>
                          <p className="text-gray-700 dark:text-gray-300">{hotel.totalRooms} rooms across {hotel.rooms.length} categories</p>
                        </div>
                      </div>

                      {/* Room types table */}
                      <div>
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Room Types</p>
                        <div className="space-y-2">
                          {hotel.rooms.map((room) => (
                            <div
                              key={room.name}
                              className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2"
                            >
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{room.name}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">{room.beds} · {room.count} available</p>
                              </div>
                              <span className="text-sm font-semibold text-accent">{room.price}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-800">
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : hotel.id)}
                      className="text-sm text-accent hover:text-accent/80 font-medium transition-colors"
                    >
                      {isExpanded ? 'View less' : 'View more'}
                    </button>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">{hotel.pricePerNight}</span>
                      <span className="text-xs text-gray-400 dark:text-gray-500">/night</span>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {filtered.length === 0 && (
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-12 text-center">
            <Hotel size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">No hotels found</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Try adjusting your search terms.</p>
          </div>
        )}
      </div>
    </div>
  )
}

function SettingsView({
  darkMode,
  setDarkMode,
  aiSuggestions,
  setAiSuggestions,
}: {
  darkMode: boolean
  setDarkMode: (v: boolean) => void
  aiSuggestions: boolean
  setAiSuggestions: (v: boolean) => void
}) {
  return (
    <div className="px-8 py-8 max-w-4xl">
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 mb-6">
        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Language</label>
          <div className="relative">
            <select className="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent/50">
              <option>English</option>
              <option>Spanish</option>
              <option>French</option>
              <option>German</option>
            </select>
            <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
          </div>
        </div>

        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm text-gray-900 dark:text-gray-100">Enable AI suggestions</span>
          <input
            type="checkbox"
            checked={aiSuggestions}
            onChange={(e) => setAiSuggestions(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-accent focus:ring-accent bg-white dark:bg-gray-800"
          />
        </label>
      </div>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 mb-6">
        <div className="flex items-start gap-4 mb-5">
          <div className="w-10 h-10 rounded-lg bg-accent-bg flex items-center justify-center flex-shrink-0">
            <Palette size={20} className="text-accent" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">Appearance</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">Customize the look and feel</p>
          </div>
        </div>

        <div className="flex items-center justify-between py-2">
          <div className="flex items-center gap-3">
            {darkMode ? (
              <Moon size={18} className="text-gray-400" />
            ) : (
              <Sun size={18} className="text-gray-400" />
            )}
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Dark Mode</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {darkMode ? 'Dark theme enabled' : 'Light theme enabled'}
              </p>
            </div>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              darkMode ? 'bg-accent' : 'bg-gray-300 dark:bg-gray-600'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                darkMode ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
        <div className="flex items-start gap-4 mb-6">
          <div className="w-10 h-10 rounded-lg bg-accent-bg flex items-center justify-center flex-shrink-0">
            <Globe size={20} className="text-accent" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">Language & Region</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">Set your language and regional preferences</p>
          </div>
        </div>

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Time Zone</label>
            <div className="relative">
              <select className="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent/50">
                <option>UTC-5 (Eastern Time)</option>
                <option>UTC-6 (Central Time)</option>
                <option>UTC-7 (Mountain Time)</option>
                <option>UTC-8 (Pacific Time)</option>
                <option>UTC+0 (Greenwich Mean Time)</option>
                <option>UTC+1 (Central European Time)</option>
              </select>
              <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Currency</label>
            <div className="relative">
              <select className="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent/50">
                <option>USD ($)</option>
                <option>EUR (€)</option>
                <option>GBP (£)</option>
                <option>JPY (¥)</option>
                <option>CAD ($)</option>
              </select>
              <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
