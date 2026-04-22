interface StepDestinationProps {
  value: string;
  onChange: (value: string) => void;
}

function StepDestination({ value, onChange }: StepDestinationProps) {
  const suggestions = [
    'Paris, France',
    'Tokyo, Japan',
    'Barcelona, Spain',
    'New York, USA',
    'Rome, Italy',
    'London, UK',
    'Dubai, UAE',
    'Sydney, Australia'
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-forge-navy mb-2">
        Where do you want to go?
      </h2>
      <p className="text-gray-600 mb-6">
        Enter your dream destination
      </p>

      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g., Paris, Tokyo, Barcelona..."
        className="input-field mb-6"
        autoFocus
      />

      <div>
        <p className="text-sm text-gray-500 mb-3">Popular destinations:</p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => onChange(suggestion)}
              className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                value === suggestion
                  ? 'bg-forge-orange text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default StepDestination;
