import { TripFormData } from '../../types/itinerary';

interface StepBudgetProps {
  value: TripFormData['budget'];
  onChange: (value: TripFormData['budget']) => void;
}

function StepBudget({ value, onChange }: StepBudgetProps) {
  const options: { value: TripFormData['budget']; label: string; desc: string; icon: string }[] = [
    {
      value: 'budget',
      label: 'Budget',
      desc: 'Hostels, street food, public transport',
      icon: '💰'
    },
    {
      value: 'mid-range',
      label: 'Mid-Range',
      desc: '3-star hotels, casual dining, mix of transport',
      icon: '💰💰'
    },
    {
      value: 'luxury',
      label: 'Luxury',
      desc: '4-5 star hotels, fine dining, private transfers',
      icon: '💰💰💰'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-forge-navy mb-2">
        What's your budget?
      </h2>
      <p className="text-gray-600 mb-6">
        This helps us tailor recommendations
      </p>

      <div className="space-y-3">
        {options.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
              value === option.value
                ? 'border-forge-orange bg-orange-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <span className="text-2xl mr-4">{option.icon}</span>
              <div>
                <div className="font-semibold text-lg">{option.label}</div>
                <div className="text-sm text-gray-600">{option.desc}</div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default StepBudget;
