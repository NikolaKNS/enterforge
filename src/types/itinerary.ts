export interface Meal {
  name: string;
  cuisine: string;
  priceRange: string;
}

export interface DayPeriod {
  activity: string;
  location: string;
  duration: string;
  tip: string;
}

export interface ItineraryDay {
  day: number;
  theme: string;
  morning: DayPeriod;
  afternoon: DayPeriod;
  evening: DayPeriod;
  meals: {
    breakfast: Meal;
    lunch: Meal;
    dinner: Meal;
  };
  transport: string;
  dailyCost: string;
  insiderTip: string;
}

export interface Itinerary {
  tripTitle: string;
  destination: string;
  totalEstimatedCost: string;
  currency: string;
  days: ItineraryDay[];
}

export interface TripFormData {
  destination: string;
  duration: number;
  budget: 'budget' | 'mid-range' | 'luxury';
  interests: string[];
  travelers: 'solo' | 'couple' | 'family' | 'friends';
}

export interface GenerateRequest {
  destination: string;
  duration: number;
  budget: string;
  interests: string[];
  travelers: string;
}

export interface GenerateResponse {
  id: string;
  itinerary: Itinerary;
}
