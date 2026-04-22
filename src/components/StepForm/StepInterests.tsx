import { TripFormData } from '../../types/itinerary';

interface StepInterestsProps {
  value: TripFormData['interests'];
  onChange: (value: TripFormData['interests']) => void;
}

function StepInterests({ value, onChange }: StepInterestsProps) {
  const options = [
    { id: 'culture', label: 'Culture & History', icon: '🏛️' },
    { id: 'food', label: 'Food & Dining', icon: '🍽️' },
    { id: 'nature', label: 'Nature & Outdoors', icon: '🌲' },
    { id: 'adventure', label: 'Adventure', icon: '🏔️' },
    { id: 'relaxation', label: 'Relaxation', icon: '🧘' },
    { id: 'nightlife', label: 'Nightlife', icon: '🌃' },
    { id: 'shopping', label: 'Shopping', icon: '🛍️' },
    { id: 'art', label: 'Art & Museums', icon: '🎨' },
    { id: 'music', label: 'Music & Shows', icon: '🎵' },
    { id: 'sports', label: 'Sports', icon: '⚽' },
    { id: 'photography', label: 'Photography', icon: '📷' },
    { id: 'wildlife', label: 'Wildlife', icon: '🦁' }
  ];

  const toggleInterest = (interest: string) => {
    if (value.includes(interest)) {
      onChange(value.filter((i) => i !== interest));
    } else {
      onChange([...value, interest]);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-forge-navy mb-2">
        What are you interested in?
      </h2>
      <p className="text-gray-600 mb-6">
        Select all that apply ({value.length} selected)
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {options.map((option) => (
          <button
            key={option.id}
            onClick={() => toggleInterest(option.id)}
            className={`p-4 rounded-xl border-2 transition-all ${
              value.includes(option.id)
                ? 'border-forge-orange bg-orange-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-2xl mb-1">{option.icon}</div>
            <div className="text-sm font-medium">{option.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default StepInterests;
