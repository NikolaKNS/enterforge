interface StepDurationProps {
  value: number;
  onChange: (value: number) => void;
}

function StepDuration({ value, onChange }: StepDurationProps) {
  const options = [3, 5, 7, 10, 14];

  return (
    <div>
      <h2 className="text-2xl font-bold text-forge-navy mb-2">
        How long is your trip?
      </h2>
      <p className="text-gray-600 mb-6">
        Select the number of days
      </p>

      <div className="grid grid-cols-3 gap-4">
        {options.map((days) => (
          <button
            key={days}
            onClick={() => onChange(days)}
            className={`p-6 rounded-xl border-2 transition-all ${
              value === days
                ? 'border-forge-orange bg-orange-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-3xl font-bold mb-1">{days}</div>
            <div className="text-gray-600">{days === 1 ? 'day' : 'days'}</div>
          </button>
        ))}
      </div>

      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Custom duration
        </label>
        <input
          type="range"
          min="1"
          max="14"
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          className="w-full accent-forge-orange"
        />
        <div className="text-center mt-2 font-semibold text-forge-orange">
          {value} {value === 1 ? 'day' : 'days'}
        </div>
      </div>
    </div>
  );
}

export default StepDuration;
