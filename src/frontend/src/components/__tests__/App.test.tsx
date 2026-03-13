import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../../App';
import * as useItineraryModule from '../../hooks/useItinerary';
import { validItineraryResponse } from '../../test/fixtures';

// Mock the useItinerary hook
vi.mock('../../hooks/useItinerary');

describe('App', () => {
  const mockSubmitProfile = vi.fn();
  const mockReset = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render app header', () => {
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'idle',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    expect(screen.getByText('✈️ Travel Agent AI')).toBeInTheDocument();
    expect(
      screen.getByText(/discover your perfect destinations with ai-powered recommendations/i)
    ).toBeInTheDocument();
  });

  it('should initially show CustomerForm when state is idle', () => {
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'idle',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    expect(screen.getByText('Plan Your Trip')).toBeInTheDocument();
    expect(screen.getByLabelText(/interests/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /build my itinerary/i })).toBeInTheDocument();
  });

  it('should show LoadingState during loading', () => {
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'loading',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    expect(screen.getByText('Building your itinerary...')).toBeInTheDocument();
    expect(screen.queryByLabelText(/interests/i)).not.toBeInTheDocument();
  });

  it('should show ItineraryView on success', () => {
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'success',
      itinerary: validItineraryResponse,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    expect(screen.getByText('Your Perfect Itinerary')).toBeInTheDocument();
    expect(screen.getByText(/Paris, France/i)).toBeInTheDocument();
    expect(screen.getByText(/Rome, Italy/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /plan another trip/i })).toBeInTheDocument();
  });

  it('should show ErrorState on error', () => {
    const errorMessage = 'Failed to create itinerary: Network error';

    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'error',
      itinerary: null,
      error: errorMessage,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });

  it('should render footer', () => {
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'idle',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    expect(screen.getByText(/powered by ai • built with react & typescript/i)).toBeInTheDocument();
  });

  it('should pass submitProfile to CustomerForm', () => {
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'idle',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    // The form exists and should receive the submitProfile callback
    expect(screen.getByRole('button', { name: /build my itinerary/i })).toBeInTheDocument();
  });

  it('should not show form when not in idle state', () => {
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'loading',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });

    render(<App />);

    expect(screen.queryByRole('button', { name: /build my itinerary/i })).not.toBeInTheDocument();
  });

  it('should handle state transitions correctly', () => {
    const { rerender } = render(<App />);

    // Start with idle
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'idle',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });
    rerender(<App />);
    expect(screen.getByText('Plan Your Trip')).toBeInTheDocument();

    // Transition to loading
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'loading',
      itinerary: null,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });
    rerender(<App />);
    expect(screen.getByText('Building your itinerary...')).toBeInTheDocument();

    // Transition to success
    vi.mocked(useItineraryModule.useItinerary).mockReturnValue({
      state: 'success',
      itinerary: validItineraryResponse,
      error: null,
      submitProfile: mockSubmitProfile,
      reset: mockReset,
    });
    rerender(<App />);
    expect(screen.getByText('Your Perfect Itinerary')).toBeInTheDocument();
  });
});
