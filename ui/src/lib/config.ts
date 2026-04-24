// TripForge API Configuration
export const config = {
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  API_KEY: import.meta.env.VITE_API_KEY || 'dev-key-change-in-production',
  AGENCY_ID: import.meta.env.VITE_AGENCY_ID || '',
} as const;

// Validate config
if (!config.AGENCY_ID) {
  console.warn('Warning: VITE_AGENCY_ID not set');
}
// Cache bust: 1777050847
