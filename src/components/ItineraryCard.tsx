import { ItineraryDay } from '../types/itinerary';

interface ItineraryCardProps {
  day: ItineraryDay;
}

function ItineraryCard({ day }: ItineraryCardProps) {
  return (
    <div className="card">
      {/* Day Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-forge-navy">
            Day {day.day}: {day.theme}
          </h3>
          <p className="text-sm text-gray-500">{day.transport}</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-forge-orange">{day.dailyCost}</p>
        </div>
      </div>

      {/* Activities */}
      <div className="space-y-4">
        {[
          { period: 'Morning', data: day.morning },
          { period: 'Afternoon', data: day.afternoon },
          { period: 'Evening', data: day.evening }
        ].map(({ period, data }) => (
          <div key={period} className="flex gap-4">
            <div className="w-20 text-sm font-medium text-gray-500">{period}</div>
            <div className="flex-1">
              <p className="font-medium">{data.activity}</p>
              <p className="text-sm text-gray-600">{data.location} • {data.duration}</p>
              <p className="text-sm text-forge-orange mt-1">💡 {data.tip}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Meals */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-sm font-medium text-gray-700 mb-2">Meals:</p>
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div>
            <p className="font-medium">{day.meals.breakfast.name}</p>
            <p className="text-gray-500">🍳 {day.meals.breakfast.cuisine} • {day.meals.breakfast.priceRange}</p>
          </div>
          <div>
            <p className="font-medium">{day.meals.lunch.name}</p>
            <p className="text-gray-500">🥪 {day.meals.lunch.cuisine} • {day.meals.lunch.priceRange}</p>
          </div>
          <div>
            <p className="font-medium">{day.meals.dinner.name}</p>
            <p className="text-gray-500">🍽️ {day.meals.dinner.cuisine} • {day.meals.dinner.priceRange}</p>
          </div>
        </div>
      </div>

      {/* Insider Tip */}
      <div className="mt-4 p-3 bg-orange-50 rounded-lg">
        <p className="text-sm">
          <span className="font-medium">Insider Tip:</span> {day.insiderTip}
        </p>
      </div>
    </div>
  );
}

export default ItineraryCard;
