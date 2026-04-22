import { useState } from 'react';
import { createCheckoutSession } from '../lib/api';

interface PaywallOverlayProps {
  dayNumber: number;
  planId: string;
  onPaymentSuccess: () => void;
}

function PaywallOverlay({ dayNumber, planId, onPaymentSuccess }: PaywallOverlayProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUnlock = async () => {
    setIsLoading(true);
    setError('');

    try {
      const { url } = await createCheckoutSession(planId);
      window.location.href = url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment failed');
      setIsLoading(false);
    }
  };

  return (
    <div className="absolute inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center rounded-xl">
      <div className="text-center p-6">
        <div className="text-4xl mb-4">🔒</div>
        <h3 className="text-xl font-bold text-forge-navy mb-2">
          Day {dayNumber} & Beyond Locked
        </h3>
        <p className="text-gray-600 mb-4">
          Upgrade to see the complete itinerary
        </p>

        <div className="space-y-2 mb-6">
          <div className="flex items-center justify-center gap-2 text-sm">
            <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Full itinerary up to 14 days
          </div>
          <div className="flex items-center justify-center gap-2 text-sm">
            <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            PDF export
          </div>
          <div className="flex items-center justify-center gap-2 text-sm">
            <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Shareable link
          </div>
        </div>

        <button
          onClick={handleUnlock}
          disabled={isLoading}
          className="btn-primary"
        >
          {isLoading ? 'Redirecting...' : 'Unlock for €4.99'}
        </button>

        {error && (
          <p className="text-red-600 text-sm mt-3">{error}</p>
        )}
      </div>
    </div>
  );
}

export default PaywallOverlay;
