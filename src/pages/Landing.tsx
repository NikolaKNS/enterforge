import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Globe,
  MapPin,
  Calendar,
  Search,
  Star,
  Compass,
  Users,
  Sparkles,
  TrendingUp
} from 'lucide-react';

function Landing() {
  const navigate = useNavigate();
  const [destination, setDestination] = useState('');
  const [dates, setDates] = useState('');

  const handleExplore = () => {
    if (destination.trim()) {
      navigate('/plan', { state: { destination } });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleExplore();
    }
  };

  return (
    <div className="min-h-screen bg-[#080d1a]">
      {/* Hero Section with Gradient Background */}
      <div
        className="relative min-h-screen"
        style={{
          background: 'linear-gradient(180deg, #0a0f2e 0%, #0d1f4e 50%, #080d1a 100%)'
        }}
      >
        {/* Navbar */}
        <nav className="absolute top-6 left-6 z-50">
          <div className="nav-pill">
            <Globe className="w-5 h-5 text-[#00b4d8]" />
            <span className="font-semibold text-white">TripForge</span>
          </div>
        </nav>

        {/* Floating Travel Photos */}
        <div className="absolute left-[5%] top-[20%] w-48 h-64 rounded-2xl overflow-hidden opacity-80 float hidden lg:block shadow-2xl shadow-black/50 border border-white/10">
          <img
            src="https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=400&h=600&fit=crop"
            alt="Travel destination"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="absolute right-[5%] top-[30%] w-48 h-64 rounded-2xl overflow-hidden opacity-80 float-delayed hidden lg:block shadow-2xl shadow-black/50 border border-white/10">
          <img
            src="https://images.unsplash.com/photo-1476514525535-07fb3c4bc5bb?w=400&h=600&fit=crop"
            alt="Travel adventure"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Hero Content */}
        <div className="container mx-auto px-4 pt-32 pb-20 flex flex-col items-center justify-center min-h-screen text-center relative z-10">
          {/* Badge */}
          <div className="badge-pill mb-8 animate-fade-in">
            <Sparkles className="w-4 h-4 text-[#00b4d8]" />
            <span>AI-Powered Trip Planning</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight">
            <span className="text-white block">Forge Your Perfect</span>
            <span className="gradient-text block">Journey</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl text-white/70 max-w-2xl mb-12 leading-relaxed">
            Discover breathtaking destinations, plan seamlessly, and create unforgettable
            adventures with intelligent travel tools
          </p>

          {/* Search Bar - Glassmorphism */}
          <div className="glass p-2 w-full max-w-3xl flex flex-col md:flex-row gap-2 mb-16">
            {/* Destination Input */}
            <div className="flex-1 flex items-center gap-3 px-4 py-3 bg-white/5 rounded-xl">
              <MapPin className="w-5 h-5 text-[#00b4d8] flex-shrink-0" />
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Where do you want to go?"
                className="w-full bg-transparent border-none outline-none text-white placeholder-white/50 text-sm"
              />
            </div>

            {/* Dates Input */}
            <div className="flex-1 flex items-center gap-3 px-4 py-3 bg-white/5 rounded-xl">
              <Calendar className="w-5 h-5 text-[#9b59b6] flex-shrink-0" />
              <input
                type="text"
                value={dates}
                onChange={(e) => setDates(e.target.value)}
                placeholder="Add dates"
                className="w-full bg-transparent border-none outline-none text-white placeholder-white/50 text-sm"
              />
            </div>

            {/* Explore Button */}
            <button
              onClick={handleExplore}
              className="btn-cyan flex items-center justify-center gap-2 min-w-[120px]"
            >
              <Search className="w-4 h-4" />
              Explore
            </button>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <section className="bg-[#080d1a] py-16 border-t border-white/5">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-[#00b4d8] mb-2">500+</div>
              <div className="text-white/60 text-sm uppercase tracking-wider">Destinations</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-[#00b4d8] mb-2">50K+</div>
              <div className="text-white/60 text-sm uppercase tracking-wider">Happy Travelers</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-[#00b4d8] mb-2 flex items-center justify-center gap-1">
                4.9<Star className="w-6 h-6 fill-[#00b4d8] text-[#00b4d8]" />
              </div>
              <div className="text-white/60 text-sm uppercase tracking-wider">Average Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Destinations Section */}
      <section className="bg-[#080d1a] py-24">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="badge-pill mb-6 inline-flex">
              <TrendingUp className="w-4 h-4 text-[#00b4d8]" />
              <span>Trending Now</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Popular Destinations
            </h2>
            <p className="text-white/60 text-lg max-w-xl mx-auto">
              Explore the world's most breathtaking places
            </p>
          </div>

          {/* Destinations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {/* Paris */}
            <div
              className="destination-card group"
              onClick={() => navigate('/plan', { state: { destination: 'Paris' } })}
            >
              <img
                src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&h=800&fit=crop"
                alt="Paris"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="flex items-center gap-2 text-[#00b4d8] text-sm mb-2">
                  <Compass className="w-4 h-4" />
                  <span>France</span>
                </div>
                <h3 className="text-2xl font-bold text-white">Paris</h3>
              </div>
            </div>

            {/* Tokyo */}
            <div
              className="destination-card group"
              onClick={() => navigate('/plan', { state: { destination: 'Tokyo' } })}
            >
              <img
                src="https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=800&fit=crop"
                alt="Tokyo"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="flex items-center gap-2 text-[#00b4d8] text-sm mb-2">
                  <Compass className="w-4 h-4" />
                  <span>Japan</span>
                </div>
                <h3 className="text-2xl font-bold text-white">Tokyo</h3>
              </div>
            </div>

            {/* New York */}
            <div
              className="destination-card group"
              onClick={() => navigate('/plan', { state: { destination: 'New York' } })}
            >
              <img
                src="https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=600&h=800&fit=crop"
                alt="New York"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="flex items-center gap-2 text-[#00b4d8] text-sm mb-2">
                  <Compass className="w-4 h-4" />
                  <span>USA</span>
                </div>
                <h3 className="text-2xl font-bold text-white">New York</h3>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Simple Pricing Section */}
      <section className="bg-[#080d1a] py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-md mx-auto">
            <div className="glass-dark p-8 text-center">
              <div className="text-sm text-[#00b4d8] uppercase tracking-wider mb-4">Pricing</div>
              <h3 className="text-3xl font-bold text-white mb-2">Simple & Transparent</h3>
              <p className="text-white/60 mb-6">No subscriptions, no hidden fees</p>

              <div className="glass p-6 mb-6">
                <div className="text-5xl font-bold text-white mb-2">
                  €4.99<span className="text-lg font-normal text-white/60">/plan</span>
                </div>
                <div className="text-white/60 text-sm">After your first free plan</div>
              </div>

              <ul className="text-left space-y-3 mb-8">
                <li className="flex items-center gap-3 text-white/80">
                  <div className="w-5 h-5 rounded-full bg-[#00b4d8]/20 flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-[#00b4d8]" />
                  </div>
                  1 free AI-generated plan
                </li>
                <li className="flex items-center gap-3 text-white/80">
                  <div className="w-5 h-5 rounded-full bg-[#00b4d8]/20 flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-[#00b4d8]" />
                  </div>
                  Full itinerary up to 14 days
                </li>
                <li className="flex items-center gap-3 text-white/80">
                  <div className="w-5 h-5 rounded-full bg-[#00b4d8]/20 flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-[#00b4d8]" />
                  </div>
                  PDF export included
                </li>
                <li className="flex items-center gap-3 text-white/80">
                  <div className="w-5 h-5 rounded-full bg-[#00b4d8]/20 flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-[#00b4d8]" />
                  </div>
                  No subscription needed
                </li>
              </ul>

              <Link
                to="/plan"
                className="btn-cyan w-full block"
              >
                Start Your Free Plan
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#080d1a] border-t border-white/5 py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Globe className="w-5 h-5 text-[#00b4d8]" />
              <span className="font-semibold text-white">TripForge</span>
            </div>
            <p className="text-white/40 text-sm">
              © 2024 TripForge. Forge your perfect journey.
            </p>
            <div className="flex items-center gap-6 text-white/40 text-sm">
              <Link to="/" className="hover:text-[#00b4d8] transition-colors">Home</Link>
              <Link to="/plan" className="hover:text-[#00b4d8] transition-colors">Plan Trip</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Landing;
