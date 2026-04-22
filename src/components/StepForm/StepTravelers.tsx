import { TripFormData } from '../../types/itinerary';

interface StepTravelersProps {
  value: TripFormData['travelers'];
  onChange: (value: TripFormData['travelers']) => void;
}

function StepTravelers({ value, onChange }: StepTravelersProps) {
  const options: { value: TripFormData['travelers']; label: string; icon: string }[] = [
    { value: 'solo', label: 'Solo', icon: '🧍' },
    { value: 'couple', label: 'Couple', icon: '💑' },
    { value: 'family', label: 'Family', icon: '👨‍👩‍👧‍👦' },
    { value: 'friends', label: 'Friends', icon: '🎉' }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-forge-navy mb-2">
        Who's traveling?
      </h2>
      <p className="text-gray-600 mb-6">
        Select your travel group
      </p>

      <div className="grid grid-cols-2 gap-4">
        {options.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`p-6 rounded-xl border-2 transition-all ${
              value === option.value
                ? 'border-forge-orange bg-orange-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-4xl mb-3">{option.icon}</div>
            <div className="font-semibold">{option.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default StepTravelers;
