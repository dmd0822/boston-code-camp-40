import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DestinationCard } from '../DestinationCard/DestinationCard';
import type { Destination } from '../../types/itinerary';
import {
  level1Advisory,
  level3Advisory,
  level4Advisory,
} from '../../test/fixtures';

describe('DestinationCard', () => {
  const baseDestination: Destination = {
    name: 'Paris',
    country: 'France',
    rationale: 'Perfect for art lovers and food enthusiasts',
    points_of_interest: [],
    events: [],
    weather: null,
  };

  it('should render destination name and country', () => {
    render(<DestinationCard destination={baseDestination} />);

    expect(screen.getByText(/Paris, France/i)).toBeInTheDocument();
  });

  it('should render rationale text', () => {
    render(<DestinationCard destination={baseDestination} />);

    expect(screen.getByText('Perfect for art lovers and food enthusiasts')).toBeInTheDocument();
  });

  it('should render points of interest list', () => {
    const destination: Destination = {
      ...baseDestination,
      points_of_interest: [
        {
          name: 'Eiffel Tower',
          description: 'Iconic iron tower',
          category: 'Landmark',
          visit_duration_hours: 2,
          source_url: 'https://example.com/eiffel',
        },
        {
          name: 'Louvre Museum',
          description: 'World-famous art museum',
          category: 'Museum',
          visit_duration_hours: 4,
          source_url: null,
        },
      ],
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.getByText('Eiffel Tower')).toBeInTheDocument();
    expect(screen.getByText('Iconic iron tower')).toBeInTheDocument();
    expect(screen.getByText('Landmark')).toBeInTheDocument();
    expect(screen.getByText(/2 hours/i)).toBeInTheDocument();

    expect(screen.getByText('Louvre Museum')).toBeInTheDocument();
    expect(screen.getByText('World-famous art museum')).toBeInTheDocument();
    expect(screen.getByText('Museum')).toBeInTheDocument();
    expect(screen.getByText(/4 hours/i)).toBeInTheDocument();
  });

  it('should render events with dates and venue', () => {
    const destination: Destination = {
      ...baseDestination,
      events: [
        {
          name: 'Summer Festival',
          dates: {
            start: '2026-07-01',
            end: '2026-07-15',
          },
          description: 'Annual summer celebration',
          venue: 'City Park',
          source_url: 'https://example.com/festival',
        },
      ],
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.getByText('Summer Festival')).toBeInTheDocument();
    expect(screen.getByText('Annual summer celebration')).toBeInTheDocument();
    expect(screen.getByText(/City Park/i)).toBeInTheDocument();
    // Check that dates are rendered (format may vary by locale)
    const datesText = screen.getByText(/📅/i).textContent;
    expect(datesText).toContain('2026');
  });

  it('should render weather forecast with temperatures', () => {
    const destination: Destination = {
      ...baseDestination,
      weather: {
        avg_high_celsius: 25,
        avg_low_celsius: 15,
        precipitation_chance: '30%',
        clothing_suggestion: 'Light jacket recommended',
        source_url: 'https://weather.example.com',
      },
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.getByText('25°C')).toBeInTheDocument();
    expect(screen.getByText('15°C')).toBeInTheDocument();
    expect(screen.getByText(/30%/)).toBeInTheDocument();
    expect(screen.getByText(/Light jacket recommended/)).toBeInTheDocument();
  });

  it('should render source URLs as links with target="_blank"', () => {
    const destination: Destination = {
      ...baseDestination,
      points_of_interest: [
        {
          name: 'Test POI',
          description: 'Test description',
          category: 'Test',
          visit_duration_hours: 1,
          source_url: 'https://poi.example.com',
        },
      ],
      events: [
        {
          name: 'Test Event',
          dates: { start: '2026-07-01', end: '2026-07-01' },
          description: 'Test event description',
          venue: 'Test Venue',
          source_url: 'https://event.example.com',
        },
      ],
      weather: {
        avg_high_celsius: 20,
        avg_low_celsius: 10,
        precipitation_chance: '10%',
        clothing_suggestion: 'Comfortable clothes',
        source_url: 'https://weather.example.com',
      },
    };

    render(<DestinationCard destination={destination} />);

    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(3);

    links.forEach(link => {
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    expect(links[0]).toHaveAttribute('href', 'https://poi.example.com');
    expect(links[1]).toHaveAttribute('href', 'https://event.example.com');
    expect(links[2]).toHaveAttribute('href', 'https://weather.example.com');
  });

  it('should handle missing weather (null)', () => {
    const destination: Destination = {
      ...baseDestination,
      weather: null,
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.queryByText(/weather forecast/i)).not.toBeInTheDocument();
  });

  it('should handle missing weather (undefined)', () => {
    const destination: Destination = {
      ...baseDestination,
      weather: undefined,
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.queryByText(/weather forecast/i)).not.toBeInTheDocument();
  });

  it('should handle empty POIs array', () => {
    const destination: Destination = {
      ...baseDestination,
      points_of_interest: [],
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.queryByText(/points of interest/i)).not.toBeInTheDocument();
  });

  it('should handle empty events array', () => {
    const destination: Destination = {
      ...baseDestination,
      events: [],
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.queryByText(/events/i)).not.toBeInTheDocument();
  });

  it('should handle singular hour in visit duration', () => {
    const destination: Destination = {
      ...baseDestination,
      points_of_interest: [
        {
          name: 'Quick Stop',
          description: 'Short visit',
          category: 'Quick',
          visit_duration_hours: 1,
          source_url: null,
        },
      ],
    };

    render(<DestinationCard destination={destination} />);

    expect(screen.getByText(/1 hour/i)).toBeInTheDocument();
    expect(screen.queryByText(/1 hours/i)).not.toBeInTheDocument();
  });

  describe('travel advisory integration', () => {
    it('should render advisory badge in the header for Level 1', () => {
      const destination: Destination = {
        ...baseDestination,
        travel_advisory: level1Advisory,
      };

      render(<DestinationCard destination={destination} />);

      expect(screen.getByText('Level 1')).toBeInTheDocument();
      expect(screen.getByText('🟢')).toBeInTheDocument();
    });

    it('should render expanded warning panel for Level 3', () => {
      const destination: Destination = {
        ...baseDestination,
        travel_advisory: level3Advisory,
      };

      render(<DestinationCard destination={destination} />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(
        screen.getByText(/level 3 — reconsider travel/i)
      ).toBeInTheDocument();
    });

    it('should render expanded warning with alternate advice for Level 4', () => {
      const destination: Destination = {
        ...baseDestination,
        travel_advisory: level4Advisory,
      };

      render(<DestinationCard destination={destination} />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(
        screen.getByText(/consider choosing an alternate location/i)
      ).toBeInTheDocument();
    });

    it('should gracefully handle missing advisory data (null)', () => {
      const destination: Destination = {
        ...baseDestination,
        travel_advisory: null,
      };

      render(<DestinationCard destination={destination} />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
      expect(screen.getByText(/Paris, France/i)).toBeInTheDocument();
    });

    it('should gracefully handle missing advisory data (undefined)', () => {
      const destination: Destination = {
        ...baseDestination,
        travel_advisory: undefined,
      };

      render(<DestinationCard destination={destination} />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
      expect(screen.getByText(/Paris, France/i)).toBeInTheDocument();
    });
  });
});
