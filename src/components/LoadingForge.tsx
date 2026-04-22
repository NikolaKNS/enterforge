function LoadingForge() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        {/* Animated Hammer */}
        <div className="relative w-24 h-24 mx-auto mb-6">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-bounce">
              <span className="text-6xl">🔨</span>
            </div>
          </div>
          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
            <div className="animate-pulse">
              <span className="text-4xl">🔥</span>
            </div>
          </div>
        </div>

        <h2 className="text-2xl font-bold text-forge-navy mb-2">
          Forging Your Journey...
        </h2>
        <p className="text-gray-600 mb-4">
          Our AI is crafting your perfect itinerary
        </p>

        {/* Loading Steps */}
        <div className="space-y-2 max-w-xs mx-auto">
          {[
            'Researching top attractions...',
            'Finding the best restaurants...',
            'Optimizing your route...',
            'Adding insider tips...'
          ].map((step, index) => (
            <div
              key={step}
              className="flex items-center text-sm text-gray-600"
              style={{
                animation: `fadeIn 0.5s ease-in ${index * 0.5}s forwards`,
                opacity: 0
              }}
            >
              <div className="w-4 h-4 mr-2 rounded-full bg-forge-orange animate-pulse" />
              {step}
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          to {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}

export default LoadingForge;
