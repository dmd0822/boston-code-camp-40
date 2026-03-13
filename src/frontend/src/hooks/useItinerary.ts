import { useState, useCallback } from 'react';
import { createItinerary } from '../api/itineraryApi';
import type { CustomerProfile, ItineraryResponse } from '../types/itinerary';

type State = 'idle' | 'loading' | 'success' | 'error';

interface UseItineraryReturn {
  state: State;
  itinerary: ItineraryResponse | null;
  error: string | null;
  submitProfile: (profile: CustomerProfile) => Promise<void>;
  reset: () => void;
}

/**
 * Custom hook for managing itinerary creation workflow.
 * Handles state transitions: idle -> loading -> success/error
 */
export function useItinerary(): UseItineraryReturn {
  const [state, setState] = useState<State>('idle');
  const [itinerary, setItinerary] = useState<ItineraryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submitProfile = useCallback(async (profile: CustomerProfile) => {
    setState('loading');
    setError(null);
    setItinerary(null);

    try {
      const response = await createItinerary(profile);
      setItinerary(response);
      setState('success');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      setState('error');
    }
  }, []);

  const reset = useCallback(() => {
    setState('idle');
    setItinerary(null);
    setError(null);
  }, []);

  return {
    state,
    itinerary,
    error,
    submitProfile,
    reset,
  };
}
