import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepDestination from '../components/StepForm/StepDestination';
import StepDuration from '../components/StepForm/StepDuration';
import StepBudget from '../components/StepForm/StepBudget';
import StepInterests from '../components/StepForm/StepInterests';
import StepTravelers from '../components/StepForm/StepTravelers';
import LoadingForge from '../components/LoadingForge';
import { TripFormData } from '../types/itinerary';
import { generateItinerary } from '../lib/api';

const steps = [
  'destination',
  'duration',
  'budget',
  'interests',
  'travelers'
] as const;

function PlanWizard() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState<TripFormData>({
    destination: '',
    duration: 7,
    budget: 'mid-range',
    interests: [],
    travelers: 'couple'
  });

  const updateField = <K extends keyof TripFormData>(
    field: K,
    value: TripFormData[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await generateItinerary({
        destination: formData.destination,
        duration: formData.duration,
        budget: formData.budget,
        interests: formData.interests,
        travelers: formData.travelers
      });

      navigate(`/result/${response.id}`, {
        state: { itinerary: response.itinerary }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate itinerary');
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingForge />;
  }

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <StepDestination
            value={formData.destination}
            onChange={(value) => updateField('destination', value)}
          />
        );
      case 1:
        return (
          <StepDuration
            value={formData.duration}
            onChange={(value) => updateField('duration', value)}
          />
        );
      case 2:
        return (
          <StepBudget
            value={formData.budget}
            onChange={(value) => updateField('budget', value)}
          />
        );
      case 3:
        return (
          <StepInterests
            value={formData.interests}
            onChange={(value) => updateField('interests', value)}
          />
        );
      case 4:
        return (
          <StepTravelers
            value={formData.travelers}
            onChange={(value) => updateField('travelers', value)}
          />
        );
      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return formData.destination.trim().length > 0;
      case 3:
        return formData.interests.length > 0;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">
              Step {currentStep + 1} of {steps.length}
            </span>
            <span className="text-sm font-medium text-forge-orange">
              {Math.round(((currentStep + 1) / steps.length) * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-forge-orange h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="card mb-6">
          {renderStep()}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className="btn-secondary"
            style={{ visibility: currentStep === 0 ? 'hidden' : 'visible' }}
          >
            Back
          </button>

          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="btn-primary"
          >
            {currentStep === steps.length - 1 ? 'Generate Itinerary' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default PlanWizard;
