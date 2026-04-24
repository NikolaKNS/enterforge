import { useState, useRef, useEffect, useCallback } from 'react'
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
  CheckCircle,
  XCircle,
  Mail,
  Link,
  AlertCircle,
  Loader2,
} from 'lucide-react'
import {
  sendChatMessage,
  getConversations,
  getConversationMessages,
  getOffers,
  approveOffer,
  rejectOffer,
  sendOffer,
  getClients,
  createClient,
  createConversation,
  type Conversation,
  type Message,
  type Offer,
  type Client,
} from './lib/api'

type View = 'agent' | 'projects' | 'arrangements' | 'clients' | 'settings'

interface Project {
  id: string
  title: string
  destination: string
  startDate: string
  endDate: string
  budget: string
  status: 'draft' | 'pending_approval' | 'approved' | 'sent' | 'rejected'
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

  const navItems: { key: View; label: string; icon: React.ElementType }[] = [
    { key: 'agent', label: 'AI Agent', icon: Bot },
    { key: 'projects', label: 'Offers', icon: Folder },
    { key: 'arrangements', label: 'Arrangements', icon: Hotel },
    { key: 'clients', label: 'Clients', icon: Users },
    { key: 'settings', label: 'Settings', icon: Settings },
  ]

  const handleEditProject = (project: Project) => {
    setSelectedProject(project)
    setActiveView('agent')
  }

  const handleCloseProject = () => {
    setSelectedProject(null)
  }

  // Check env vars
  const hasApiUrl = !!import.meta.env.VITE_API_URL;
  const hasAgencyId = !!import.meta.env.VITE_AGENCY_ID;
  const hasApiKey = !!import.meta.env.VITE_API_KEY;
  const configError = !hasApiUrl || !hasAgencyId || !hasApiKey;

  return (
    <div className={`flex h-screen w-full ${darkMode ? 'dark' : ''}`}>
      <div className="flex h-screen w-full bg-gray-50 dark:bg-gray-950">
        {/* Config Error Banner */}
        {configError && (
          <div className="fixed top-0 left-0 right-0 z-50 bg-red-600 text-white px-4 py-2 text-sm">
            <strong>Configuration Error:</strong>{' '}
            {!hasApiUrl && 'VITE_API_URL missing '}{' '}
            {!hasAgencyId && 'VITE_AGENCY_ID missing '}{' '}
            {!hasApiKey && 'VITE_API_KEY missing '}
            (check .env file and restart)
          </div>
        )}
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
              selectedProject={selectedProject}
              onCloseProject={handleCloseProject}
              inputRef={inputRef}
            />
          ) : activeView === 'projects' ? (
            <ProjectsView onEdit={handleEditProject} />
          ) : activeView === 'arrangements' ? (
            <ArrangementsView />
          ) : activeView === 'clients' ? (
            <ClientsView />
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

// Agent View with Chat
function AgentView({
  inputValue,
  setInputValue,
  selectedProject,
  onCloseProject,
  inputRef,
}: {
  inputValue: string
  setInputValue: (v: string) => void
  selectedProject: Project | null
  onCloseProject: () => void
  inputRef: React.RefObject<HTMLInputElement | null>
}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversation, setActiveConversation] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const data = await getConversations()
      setConversations(data.conversations)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    }
  }

  const loadMessages = async (conversationId: string) => {
    try {
      setLoading(true)
      const data = await getConversationMessages(conversationId)
      setMessages(data.messages)
      setActiveConversation(conversationId)
      setError(null)
    } catch (err) {
      setError('Failed to load messages')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const message = inputValue.trim()
    setInputValue('')
    setLoading(true)
    setError(null)

    try {
      // Create conversation if none exists
      let conversationId = activeConversation
      if (!conversationId) {
        const newConv = await createConversation(message.slice(0, 50))
        conversationId = newConv.id
        setActiveConversation(conversationId)
        await loadConversations()
      }

      const response = await sendChatMessage(
        message,
        conversationId,
        selectedProject ? { project_id: selectedProject.id } : undefined
      )

      // Reload messages to show the full conversation
      await loadMessages(conversationId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  const startNewConversation = () => {
    setActiveConversation(null)
    setMessages([])
    setError(null)
  }

  const actions = [
    { icon: Package, label: 'Create a new offer', onClick: startNewConversation },
    { icon: Users, label: 'Find customer bookings' },
    { icon: TrendingUp, label: 'Analyze sales trends' },
    { icon: Compass, label: 'Suggest destinations' },
  ]

  return (
    <div className="flex h-full">
      {/* Conversations Sidebar */}
      {sidebarOpen && (
        <div className="w-64 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex flex-col">
          <div className="p-4 border-b border-gray-200 dark:border-gray-800">
            <button
              onClick={startNewConversation}
              className="w-full flex items-center justify-center gap-2 bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent/90 transition-colors font-medium"
            >
              <Sparkles size={16} />
              New Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => loadMessages(conv.id)}
                className={`w-full text-left p-3 rounded-lg mb-1 transition-colors ${
                  activeConversation === conv.id
                    ? 'bg-accent-bg border border-accent/20'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {conv.title}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {conv.status === 'active' ? '🟢 Active' : conv.status === 'pending_approval' ? '🟡 Pending' : '⚪ Closed'}
                </p>
              </button>
            ))}
            {conversations.length === 0 && (
              <p className="text-sm text-gray-400 text-center py-4">No conversations yet</p>
            )}
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 border-t border-gray-200 dark:border-gray-800 text-gray-400 hover:text-gray-600"
          >
            ← Hide
          </button>
        </div>
      )}

      <div className="flex-1 flex flex-col">
        {/* Toggle sidebar button when closed */}
        {!sidebarOpen && (
          <button
            onClick={() => setSidebarOpen(true)}
            className="absolute left-4 top-4 z-10 p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm"
          >
            <Clock size={16} />
          </button>
        )}

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
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {activeConversation ? 'Continue your conversation' : 'Start a new conversation'}
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="px-8 pb-4">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3">
              <AlertCircle size={20} className="text-red-500" />
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
              <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-700">
                <X size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Action Cards */}
        {!activeConversation && messages.length === 0 && (
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
        )}

        {/* Chat Area */}
        <div className="flex-1 px-8 py-6">
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl h-full flex flex-col">
            <div className="flex-1 p-6 overflow-y-auto">
              {messages.length === 0 ? (
                <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-5 max-w-3xl">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles size={16} className="text-accent" />
                    <span className="text-sm font-medium text-accent">AI Assistant</span>
                  </div>
                  <p className="text-gray-800 dark:text-gray-200 text-sm leading-relaxed">
                    Hello! I&apos;m your AI travel assistant. I can help you create travel offers, manage customer bookings,
                    analyze trends, and answer questions about your travel agency operations. How can I assist you today?
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-3xl rounded-xl p-4 ${
                          msg.role === 'user'
                            ? 'bg-accent text-white'
                            : msg.role === 'tool'
                            ? 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'
                            : 'bg-gray-100 dark:bg-gray-800'
                        }`}
                      >
                        {msg.role === 'assistant' && (
                          <div className="flex items-center gap-2 mb-2">
                            <Sparkles size={14} className="text-accent" />
                            <span className="text-xs font-medium text-accent">AI Assistant</span>
                          </div>
                        )}
                        {msg.role === 'tool' && (
                          <div className="flex items-center gap-2 mb-2">
                            <CheckCircle size={14} className="text-yellow-600" />
                            <span className="text-xs font-medium text-yellow-700 dark:text-yellow-400">Tool Result</span>
                          </div>
                        )}
                        <p className={`text-sm leading-relaxed ${
                          msg.role === 'user' ? 'text-white' : 'text-gray-800 dark:text-gray-200'
                        }`}>
                          {msg.content}
                        </p>
                        {msg.model && (
                          <p className="text-xs text-gray-400 mt-2">Model: {msg.model}</p>
                        )}
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4 flex items-center gap-3">
                        <Loader2 size={16} className="animate-spin text-accent" />
                        <span className="text-sm text-gray-500">AI is thinking...</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-800">
              <div className="flex gap-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={
                    selectedProject
                      ? `Editing "${selectedProject.title}" — ask the AI to modify this offer...`
                      : "Ask me anything about your travel agency..."
                  }
                  disabled={loading}
                  className="flex-1 px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-50"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={loading || !inputValue.trim()}
                  className="bg-accent hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-3 rounded-lg flex items-center gap-2 transition-colors font-medium"
                >
                  {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Projects View - Shows Offers
function ProjectsView({ onEdit }: { onEdit: (project: Project) => void }) {
  const [offers, setOffers] = useState<Offer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('')

  useEffect(() => {
    loadOffers()
  }, [filter])

  const loadOffers = async () => {
    try {
      setLoading(true)
      const data = await getOffers(filter || undefined)
      setOffers(data.offers)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load offers')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (offerId: string) => {
    try {
      await approveOffer(offerId, 'current-user')
      await loadOffers()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to approve')
    }
  }

  const handleReject = async (offerId: string) => {
    const reason = prompt('Enter rejection reason:')
    if (!reason) return
    try {
      await rejectOffer(offerId, reason)
      await loadOffers()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to reject')
    }
  }

  const handleSend = async (offerId: string) => {
    try {
      await sendOffer(offerId, 'email')
      await loadOffers()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to send')
    }
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    pending_approval: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    approved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    sent: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  }

  const statusLabels: Record<string, string> = {
    draft: 'Draft',
    pending_approval: 'Pending Approval',
    approved: 'Approved',
    rejected: 'Rejected',
    sent: 'Sent to Client',
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-8 pt-8 pb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Travel Offers</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Manage AI-generated travel offers</p>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="pending_approval">Pending Approval</option>
            <option value="approved">Approved</option>
            <option value="sent">Sent</option>
          </select>
          <button
            onClick={loadOffers}
            className="p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Clock size={16} />
          </button>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {offers.length} offer{offers.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      {error && (
        <div className="px-8 pb-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle size={20} className="text-red-500" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 size={32} className="animate-spin text-accent" />
        </div>
      ) : (
        <div className="px-8 pb-8">
          {offers.length === 0 ? (
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-12 text-center">
              <Package size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">No offers yet</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Use the AI Agent to create your first travel offer.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {offers.map((offer) => (
                <div
                  key={offer.id}
                  className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">{offer.title}</h3>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColors[offer.status]}`}>
                      {statusLabels[offer.status]}
                    </span>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-3 text-sm">
                      <MapPin size={16} className="text-gray-400" />
                      <span className="text-gray-700 dark:text-gray-300">{offer.destination}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm">
                      <DollarSign size={16} className="text-gray-400" />
                      <span className="text-gray-700 dark:text-gray-300">
                        {offer.pricing?.total} {offer.pricing?.currency}
                      </span>
                    </div>
                    {offer.valid_until && (
                      <div className="flex items-center gap-3 text-sm">
                        <Calendar size={16} className="text-gray-400" />
                        <span className="text-gray-700 dark:text-gray-300">Valid until: {offer.valid_until}</span>
                      </div>
                    )}
                  </div>

                  {offer.status === 'pending_approval' && (
                    <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                      <button
                        onClick={() => handleApprove(offer.id)}
                        className="flex-1 flex items-center justify-center gap-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                      >
                        <CheckCircle size={16} />
                        Approve
                      </button>
                      <button
                        onClick={() => handleReject(offer.id)}
                        className="flex-1 flex items-center justify-center gap-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                      >
                        <XCircle size={16} />
                        Reject
                      </button>
                    </div>
                  )}

                  {offer.status === 'approved' && (
                    <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                      <button
                        onClick={() => handleSend(offer.id)}
                        className="w-full flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                      >
                        <Mail size={16} />
                        Send to Client
                      </button>
                    </div>
                  )}

                  {offer.status === 'sent' && (
                    <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 flex items-center gap-2 text-blue-600">
                      <CheckCircle size={16} />
                      <span className="text-sm">Sent via {offer.sent_method}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Clients View
function ClientsView() {
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newClient, setNewClient] = useState({ name: '', email: '', phone: '' })

  useEffect(() => {
    loadClients()
  }, [])

  const loadClients = async () => {
    try {
      setLoading(true)
      const data = await getClients()
      setClients(data.clients)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load clients')
    } finally {
      setLoading(false)
    }
  }

  const handleAddClient = async () => {
    try {
      await createClient(newClient)
      setShowAddModal(false)
      setNewClient({ name: '', email: '', phone: '' })
      await loadClients()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create client')
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-8 pt-8 pb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Clients</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Manage your customer database</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-accent hover:bg-accent/90 text-white px-4 py-2 rounded-lg font-medium"
        >
          <Users size={16} />
          Add Client
        </button>
      </div>

      {error && (
        <div className="px-8 pb-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle size={20} className="text-red-500" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 size={32} className="animate-spin text-accent" />
        </div>
      ) : (
        <div className="px-8 pb-8">
          {clients.length === 0 ? (
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-12 text-center">
              <Users size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">No clients yet</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Add your first client to get started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {clients.map((client) => (
                <div
                  key={client.id}
                  className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-full bg-accent-bg flex items-center justify-center">
                      <User size={20} className="text-accent" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-gray-100">{client.name}</h3>
                      <p className="text-xs text-gray-500">{client.email}</p>
                    </div>
                  </div>
                  {client.phone && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      📞 {client.phone}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Add Client Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Add New Client</h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Name"
                value={newClient.name}
                onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700"
              />
              <input
                type="email"
                placeholder="Email"
                value={newClient.email}
                onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700"
              />
              <input
                type="tel"
                placeholder="Phone (optional)"
                value={newClient.phone}
                onChange={(e) => setNewClient({ ...newClient, phone: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700"
              />
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleAddClient}
                className="flex-1 px-4 py-2 rounded-lg bg-accent text-white"
              >
                Add Client
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Arrangements View (Hotels - Static for now)
function ArrangementsView() {
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
      ],
    },
  ]

  return (
    <div className="flex flex-col h-full">
      <div className="px-8 pt-8 pb-6">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Arrangements</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Hotels and accommodations in our network</p>
      </div>

      <div className="px-8 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {hotels.map((hotel) => (
            <div
              key={hotel.id}
              className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden"
            >
              <div className={`h-32 bg-gradient-to-br ${hotel.imageGradient} flex items-center justify-center`}>
                <Hotel size={32} className="text-white/80" />
              </div>
              <div className="p-4">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{hotel.name}</h3>
                <div className="flex items-center gap-1.5 mt-2">
                  <MapPin size={13} className="text-gray-400" />
                  <span className="text-xs text-gray-500">{hotel.location}</span>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <Star size={14} className="text-amber-400 fill-amber-400" />
                  <span className="text-sm font-medium">{hotel.rating}</span>
                  <span className="text-xs text-gray-400">({hotel.reviews} reviews)</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Settings View
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
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">Appearance</h3>
        <div className="flex items-center justify-between py-2">
          <div className="flex items-center gap-3">
            {darkMode ? <Moon size={18} className="text-gray-400" /> : <Sun size={18} className="text-gray-400" />}
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Dark Mode</span>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              darkMode ? 'bg-accent' : 'bg-gray-300'
            }`}
          >
            <span className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
              darkMode ? 'translate-x-6' : 'translate-x-1'
            }`} />
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 mb-6">
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">AI Settings</h3>
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm text-gray-900 dark:text-gray-100">Enable AI suggestions</span>
          <input
            type="checkbox"
            checked={aiSuggestions}
            onChange={(e) => setAiSuggestions(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-accent focus:ring-accent"
          />
        </label>
      </div>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">API Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">API URL</label>
            <input
              type="text"
              value={import.meta.env.VITE_API_URL || 'http://localhost:8000'}
              readOnly
              className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Agency ID</label>
            <input
              type="text"
              value={import.meta.env.VITE_AGENCY_ID || 'Not set'}
              readOnly
              className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
