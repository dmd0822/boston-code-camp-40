import type { CustomerProfile, ItineraryResponse } from '../types/itinerary';

/**
 * API client for the Travel Agent backend.
 * Uses native fetch with relative URLs that will be proxied by Vite.
 */

interface HealthResponse {
  status: string;
  version: string;
}

/**
 * Creates an itinerary based on a customer profile.
 * POST /api/itinerary
 */
export async function createItinerary(profile: CustomerProfile): Promise<ItineraryResponse> {
  const response = await fetch('/api/itinerary', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    const errorText = await response.text();
    let errorMessage = `Failed to create itinerary: ${response.status} ${response.statusText}`;
    
    try {
      const errorData = JSON.parse(errorText);
      if (errorData.detail) {
        errorMessage = `Failed to create itinerary: ${errorData.detail}`;
      }
    } catch {
      // If not JSON, use the text if available
      if (errorText) {
        errorMessage = `Failed to create itinerary: ${errorText}`;
      }
    }
    
    throw new Error(errorMessage);
  }

  return response.json();
}

/**
 * Checks the health status of the backend API.
 * GET /api/health
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch('/api/health', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
