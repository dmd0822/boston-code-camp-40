import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ItineraryView } from '../ItineraryView/ItineraryView';
import { validItineraryResponse } from '../../test/fixtures';

describe('ItineraryView', () => {
  it('should render all destinations', () => {
    render(<ItineraryView itinerary={validItineraryResponse} />);

    expect(screen.getByText(/Paris, France/i)).toBeInTheDocument();
    expect(screen.getByText(/Rome, Italy/i)).toBeInTheDocument();
  });

  it('should render generated_at timestamp', () => {
    render(<ItineraryView itinerary={validItineraryResponse} />);

    // The timestamp is formatted using toLocaleString, so we check for part of it
    expect(screen.getByText(/generated on/i)).toBeInTheDocument();
  });

  it('should render correct number of DestinationCards', () => {
    render(<ItineraryView itinerary={validItineraryResponse} />);

    // Check that we have 2 destinations rendered - text may be split across elements
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText(/destinations curated for you/i)).toBeInTheDocument();
  });

  it('should render title', () => {
    render(<ItineraryView itinerary={validItineraryResponse} />);

    expect(screen.getByText('Your Perfect Itinerary')).toBeInTheDocument();
  });

  it('should use singular "destination" for single destination', () => {
    const singleDestinationResponse = {
      ...validItineraryResponse,
      destinations: [validItineraryResponse.destinations[0]],
    };

    render(<ItineraryView itinerary={singleDestinationResponse} />);

    // Check for singular form - text may be split across elements
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText(/destination curated for you/i)).toBeInTheDocument();
  });

  it('should render POIs from destinations', () => {
    render(<ItineraryView itinerary={validItineraryResponse} />);

    // Check POIs from Paris
    expect(screen.getByText('Eiffel Tower')).toBeInTheDocument();
    expect(screen.getByText('Louvre Museum')).toBeInTheDocument();

    // Check POIs from Rome
    expect(screen.getByText('Colosseum')).toBeInTheDocument();
    expect(screen.getByText('Vatican Museums')).toBeInTheDocument();
  });

  it('should render events from destinations', () => {
    render(<ItineraryView itinerary={validItineraryResponse} />);

    expect(screen.getByText('Fête de la Musique')).toBeInTheDocument();
    expect(screen.getByText('Estate Romana')).toBeInTheDocument();
  });

  it('should render weather information from destinations', () => {
    render(<ItineraryView itinerary={validItineraryResponse} />);

    // Paris weather
    expect(screen.getByText('24°C')).toBeInTheDocument();
    expect(screen.getByText('15°C')).toBeInTheDocument();

    // Rome weather
    expect(screen.getByText('28°C')).toBeInTheDocument();
    expect(screen.getByText('18°C')).toBeInTheDocument();
  });
});
