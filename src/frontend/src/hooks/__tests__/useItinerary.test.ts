import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useItinerary } from '../useItinerary';
import { validCustomerProfile, validItineraryResponse } from '../../test/fixtures';
import * as itineraryApi from '../../api/itineraryApi';

// Mock the API module
vi.mock('../../api/itineraryApi');

describe('useItinerary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should have initial state as idle', () => {
    const { result } = renderHook(() => useItinerary());

    expect(result.current.state).toBe('idle');
    expect(result.current.itinerary).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should transition to loading then success on successful submission', async () => {
    vi.mocked(itineraryApi.createItinerary).mockResolvedValue(validItineraryResponse);

    const { result } = renderHook(() => useItinerary());

    // Submit the profile
    await result.current.submitProfile(validCustomerProfile);

    // After completion, should be in success state
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

    // Submit the profile
    await result.current.submitProfile(validCustomerProfile);

    // After completion, should be in error state
    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe(errorMessage);
    expect(result.current.itinerary).toBeNull();
  });

  it('should handle non-Error thrown values', async () => {
    vi.mocked(itineraryApi.createItinerary).mockRejectedValue('String error');

    const { result } = renderHook(() => useItinerary());

    result.current.submitProfile(validCustomerProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe('An unexpected error occurred');
    expect(result.current.itinerary).toBeNull();
  });

  it('should reset to idle state', async () => {
    vi.mocked(itineraryApi.createItinerary).mockResolvedValue(validItineraryResponse);

    const { result } = renderHook(() => useItinerary());

    // Submit and wait for success
    await result.current.submitProfile(validCustomerProfile);
    await waitFor(() => {
      expect(result.current.state).toBe('success');
    });

    // Reset
    act(() => {
      result.current.reset();
    });

    // Check state after reset
    expect(result.current.state).toBe('idle');
    expect(result.current.itinerary).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should make itinerary available after success', async () => {
    vi.mocked(itineraryApi.createItinerary).mockResolvedValue(validItineraryResponse);

    const { result } = renderHook(() => useItinerary());

    result.current.submitProfile(validCustomerProfile);

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

    result.current.submitProfile(validCustomerProfile);

    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe(errorMessage);
  });

  it('should clear error when submitting again', async () => {
    // First submission fails
    vi.mocked(itineraryApi.createItinerary).mockRejectedValueOnce(new Error('First error'));

    const { result } = renderHook(() => useItinerary());

    await result.current.submitProfile(validCustomerProfile);
    await waitFor(() => {
      expect(result.current.state).toBe('error');
    });

    expect(result.current.error).toBe('First error');

    // Second submission succeeds
    vi.mocked(itineraryApi.createItinerary).mockResolvedValueOnce(validItineraryResponse);

    await result.current.submitProfile(validCustomerProfile);

    // Should transition through loading to success, clearing error
    await waitFor(() => {
      expect(result.current.state).toBe('success');
    });

    expect(result.current.error).toBeNull();
    expect(result.current.itinerary).toEqual(validItineraryResponse);
  });
});
