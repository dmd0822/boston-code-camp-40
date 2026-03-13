import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as itineraryApi from '../../api/itineraryApi';
import { validCustomerProfile, validItineraryResponse } from '../../test/fixtures';
import { useItinerary } from '../useItinerary';

vi.mock('../../api/itineraryApi');

describe('useItinerary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  async function submitProfile(
    submit: (profile: typeof validCustomerProfile) => Promise<void>
  ) {
    await act(async () => {
      await submit(validCustomerProfile);
    });
  }

  it('should have initial state as idle', () => {
    const { result } = renderHook(() => useItinerary());

    expect(result.current.state).toBe('idle');
    expect(result.current.itinerary).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should transition to loading then success on successful submission', async () => {
    vi.mocked(itineraryApi.createItinerary).mockResolvedValue(validItineraryResponse);

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('success');
    });

    expect(result.current.itinerary).toEqual(validItineraryResponse);
    expect(result.current.error).toBeNull();
    expect(itineraryApi.createItinerary).toHaveBeenCalledWith(validCustomerProfile);
  });

  it('should transition to loading then error on API failure', async () => {
    const errorMessage = 'Failed to create itinerary: Network error';
    vi.mocked(itineraryApi.createItinerary).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe(errorMessage);
    expect(result.current.itinerary).toBeNull();
  });

  it('should handle non-Error thrown values', async () => {
    vi.mocked(itineraryApi.createItinerary).mockRejectedValue('String error');

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe('An unexpected error occurred');
    expect(result.current.itinerary).toBeNull();
  });

  it('should reset to idle state', async () => {
    vi.mocked(itineraryApi.createItinerary).mockResolvedValue(validItineraryResponse);

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);
    await waitFor(() => {
      expect(result.current.state).toBe('success');
    });

    act(() => {
      result.current.reset();
    });

    expect(result.current.state).toBe('idle');
    expect(result.current.itinerary).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should make itinerary available after success', async () => {
    vi.mocked(itineraryApi.createItinerary).mockResolvedValue(validItineraryResponse);

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('success');
    });

    expect(result.current.itinerary).not.toBeNull();
    expect(result.current.itinerary?.destinations).toHaveLength(2);
    expect(result.current.itinerary?.generated_at).toBe('2026-05-15T14:30:00Z');
  });

  it('should make error message available after failure', async () => {
    const errorMessage = 'Failed to create itinerary: Invalid budget';
    vi.mocked(itineraryApi.createItinerary).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe(errorMessage);
  });

  it('should clear error when submitting again', async () => {
    vi.mocked(itineraryApi.createItinerary).mockRejectedValueOnce(new Error('First error'));

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);
    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe('First error');

    vi.mocked(itineraryApi.createItinerary).mockResolvedValueOnce(validItineraryResponse);

    await submitProfile(result.current.submitProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('success');
    });

    expect(result.current.error).toBeNull();
    expect(result.current.itinerary).toEqual(validItineraryResponse);
  });

  it('retries the last submitted profile after an error', async () => {
    vi.mocked(itineraryApi.createItinerary)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce(validItineraryResponse);

    const { result } = renderHook(() => useItinerary());

    await submitProfile(result.current.submitProfile);
    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    await act(async () => {
      await result.current.retryLastSubmission();
    });

    await waitFor(() => {
      expect(result.current.state).toBe('success');
    });

    expect(itineraryApi.createItinerary).toHaveBeenNthCalledWith(1, validCustomerProfile);
    expect(itineraryApi.createItinerary).toHaveBeenNthCalledWith(2, validCustomerProfile);
  });
});
