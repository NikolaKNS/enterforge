import Anthropic from '@anthropic-ai/sdk';
import dotenv from 'dotenv';

dotenv.config();

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || ''
});

const SYSTEM_PROMPT = `You are an expert travel planner with deep knowledge of destinations worldwide.
Create detailed, personalized, and practical travel itineraries.
Always use real, specific restaurant and attraction names.
Return ONLY valid JSON. No markdown, no explanation, no extra text.`;

interface GenerateItineraryParams {
  destination: string;
  duration: number;
  budget: string;
  interests: string[];
  travelers: string;
}

export async function generateItinerary(params: GenerateItineraryParams) {
  const { destination, duration, budget, interests, travelers } = params;

  const userPrompt = `Create a ${duration}-day travel itinerary for ${destination}.
Travelers: ${travelers}
Budget: ${budget}
Interests: ${interests.join(', ')}

Return ONLY this JSON structure:
{
  "tripTitle": "string",
  "destination": "string",
  "totalEstimatedCost": "string",
  "currency": "EUR",
  "days": [
    {
      "day": 1,
      "theme": "string",
      "morning": { "activity": "string", "location": "string", "duration": "string", "tip": "string" },
      "afternoon": { "activity": "string", "location": "string", "duration": "string", "tip": "string" },
      "evening": { "activity": "string", "location": "string", "duration": "string", "tip": "string" },
      "meals": {
        "breakfast": { "name": "string", "cuisine": "string", "priceRange": "€" },
        "lunch": { "name": "string", "cuisine": "string", "priceRange": "€" },
        "dinner": { "name": "string", "cuisine": "string", "priceRange": "€" }
      },
      "transport": "string",
      "dailyCost": "string",
      "insiderTip": "string"
    }
  ]
}`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4000,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: userPrompt
      }
    ]
  });

  const content = response.content[0];
  if (content.type !== 'text') {
    throw new Error('Unexpected response type from Claude');
  }

  // Parse the JSON response
  try {
    const itinerary = JSON.parse(content.text);
    return itinerary;
  } catch (error) {
    throw new Error('Failed to parse itinerary JSON from Claude');
  }
}
