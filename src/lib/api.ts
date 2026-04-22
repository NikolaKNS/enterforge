import { GenerateRequest, GenerateResponse } from '../types/itinerary';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001';

export async function generateItinerary(data: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to generate itinerary');
  }

  return response.json();
}

export async function createCheckoutSession(planId: string): Promise<{ url: string }> {
  const response = await fetch(`${API_BASE}/api/payment/create-checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ planId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to create checkout session');
  }

  return response.json();
}

export async function verifyPayment(sessionId: string): Promise<{ paid: boolean; planId: string }> {
  const response = await fetch(
    `${API_BASE}/api/payment/verify?session_id=${sessionId}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to verify payment');
  }

  return response.json();
}
