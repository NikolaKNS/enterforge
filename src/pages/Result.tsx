import { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import ItineraryCard from '../components/ItineraryCard';
import PaywallOverlay from '../components/PaywallOverlay';
import PDFExport from '../components/PDFExport';
import { Itinerary } from '../types/itinerary';

const FREE_DAY_LIMIT = 3;

interface LocationState {
  itinerary: Itinerary;
}

function Result() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const [isPaid, setIsPaid] = useState(false);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check URL params for payment success
    const urlParams = new URLSearchParams(window.location.search);
    const paymentStatus = urlParams.get('payment');

    if (paymentStatus === 'success') {
      setIsPaid(true);
      // Remove query params
      window.history.replaceState({}, '', `/result/${id}`);
    }

    // Get itinerary from navigation state or fetch from API
    const state = location.state as LocationState;
    if (state?.itinerary) {
      setItinerary(state.itinerary);
      setIsLoading(false);
    } else {
      // TODO: Fetch from API using the ID
      setIsLoading(false);
    }
  }, [id, location.state]);

  const handlePaymentSuccess = () => {
    setIsPaid(true);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forge-orange mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your itinerary...</p>
        </div>
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Itinerary not found</p>
          <a href="/" className="btn-primary">
            Go Home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-forge-navy mb-2">
                {itinerary.tripTitle}
              </h1>
              <p className="text-gray-600">
                {itinerary.destination} • {itinerary.days.length} days • Est. {itinerary.totalEstimatedCost} {itinerary.currency}
              </p>
            </div>

            {isPaid && <PDFExport itinerary={itinerary} />}
          </div>
        </div>

        {/* Itinerary Days */}
        <div className="space-y-6">
          {itinerary.days.map((day, index) => {
            const isLocked = !isPaid && index >= FREE_DAY_LIMIT;

            return (
              <div key={day.day} className="relative">
                <ItineraryCard day={day} />
                {isLocked && (
                  <PaywallOverlay
                    dayNumber={day.day}
                    planId={id || ''}
                    onPaymentSuccess={handlePaymentSuccess}
                  />
                )}
              </div>
            );
          })}
        </div>

        {/* Upgrade CTA for Free Users */}
        {!isPaid && itinerary.days.length > FREE_DAY_LIMIT && (
          <div className="mt-8 text-center">
            <p className="text-gray-600 mb-4">
              Want to see the full {itinerary.days.length}-day itinerary?
            </p>
            <button className="btn-primary">
              Unlock Full Plan - €4.99
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Result;
