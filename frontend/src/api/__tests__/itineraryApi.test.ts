import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createItinerary, getHealth } from '../itineraryApi';
import { validCustomerProfile, validItineraryResponse } from '../../test/fixtures';

describe('itineraryApi', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.restoreAllMocks();
  });

  describe('createItinerary', () => {
    it('should send correct POST request with CustomerProfile body', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => validItineraryResponse,
      });
      global.fetch = mockFetch;

      await createItinerary(validCustomerProfile);

      expect(mockFetch).toHaveBeenCalledWith('/api/itinerary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(validCustomerProfile),
      });
    });

    it('should return parsed ItineraryResponse on success', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => validItineraryResponse,
      });

      const result = await createItinerary(validCustomerProfile);

      expect(result).toEqual(validItineraryResponse);
      expect(result.destinations).toHaveLength(2);
      expect(result.destinations[0].name).toBe('Paris');
    });

    it('should include correct Content-Type header', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => validItineraryResponse,
      });
      global.fetch = mockFetch;

      await createItinerary(validCustomerProfile);

      const callArgs = mockFetch.mock.calls[0];
      expect(callArgs[1].headers['Content-Type']).toBe('application/json');
    });

    it('should throw on non-OK response with status text', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => '',
      });

      await expect(createItinerary(validCustomerProfile)).rejects.toThrow(
        'Failed to create itinerary: 500 Internal Server Error'
      );
    });

    it('should throw with detailed error message from JSON response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => JSON.stringify({ detail: 'Invalid customer profile data' }),
      });

      await expect(createItinerary(validCustomerProfile)).rejects.toThrow(
        'Failed to create itinerary: Invalid customer profile data'
      );
    });

    it('should throw with error text when not JSON', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        text: async () => 'Service temporarily unavailable',
      });

      await expect(createItinerary(validCustomerProfile)).rejects.toThrow(
        'Failed to create itinerary: Service temporarily unavailable'
      );
    });
  });

  describe('getHealth', () => {
    it('should return health response on success', async () => {
      const healthResponse = {
        status: 'healthy',
        version: '1.0.0',
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => healthResponse,
      });

      const result = await getHealth();

      expect(result).toEqual(healthResponse);
      expect(result.status).toBe('healthy');
    });

    it('should send GET request to /api/health', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'healthy', version: '1.0.0' }),
      });
      global.fetch = mockFetch;

      await getHealth();

      expect(mockFetch).toHaveBeenCalledWith('/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('should throw on error response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
      });

      await expect(getHealth()).rejects.toThrow(
        'Health check failed: 503 Service Unavailable'
      );
    });
  });
});
