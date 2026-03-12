import type { CustomerProfile, ItineraryResponse } from '../types/itinerary';

/**
 * Test fixtures for reusable test data.
 * Contains realistic travel data for consistent testing.
 */

export const validCustomerProfile: CustomerProfile = {
  interests: ['history', 'food', 'architecture'],
  budget: 'moderate',
  travel_dates: {
    start: '2026-06-01',
    end: '2026-06-15',
  },
  party_size: 2,
  departure_city: 'Boston',
  notes: 'Looking for a romantic getaway with cultural experiences',
};

export const validItineraryResponse: ItineraryResponse = {
  destinations: [
    {
      name: 'Paris',
      country: 'France',
      rationale:
        'Perfect blend of history, cuisine, and iconic architecture. The city offers world-class museums, romantic ambiance, and unforgettable dining experiences.',
      points_of_interest: [
        {
          name: 'Eiffel Tower',
          description: 'Iconic iron lattice tower offering panoramic views of Paris',
          category: 'Landmark',
          visit_duration_hours: 2,
          source_url: 'https://www.toureiffel.paris/en',
        },
        {
          name: 'Louvre Museum',
          description: 'World-renowned art museum featuring the Mona Lisa and thousands of masterpieces',
          category: 'Museum',
          visit_duration_hours: 4,
          source_url: 'https://www.louvre.fr/en',
        },
        {
          name: 'Notre-Dame Cathedral',
          description: 'Gothic architectural masterpiece on Île de la Cité',
          category: 'Religious Site',
          visit_duration_hours: 1,
          source_url: 'https://www.notredamedeparis.fr/en/',
        },
      ],
      events: [
        {
          name: 'Fête de la Musique',
          dates: {
            start: '2026-06-21',
            end: '2026-06-21',
          },
          description: 'Annual music festival celebrating the summer solstice with free concerts throughout the city',
          venue: 'Various locations across Paris',
          source_url: 'https://fetedelamusique.culture.gouv.fr/',
        },
      ],
      weather: {
        avg_high_celsius: 24,
        avg_low_celsius: 15,
        precipitation_chance: '30%',
        clothing_suggestion: 'Light layers with a jacket for evenings',
        source_url: 'https://www.weather.com/weather/monthly/l/Paris+France',
      },
    },
    {
      name: 'Rome',
      country: 'Italy',
      rationale:
        'Ancient history comes alive in this eternal city. Experience incredible Roman ruins, world-famous cuisine, and Renaissance art.',
      points_of_interest: [
        {
          name: 'Colosseum',
          description: 'Ancient amphitheater and iconic symbol of Imperial Rome',
          category: 'Historical Site',
          visit_duration_hours: 3,
          source_url: 'https://www.il-colosseo.it/en/',
        },
        {
          name: 'Vatican Museums',
          description: 'Vast collection of art and historical artifacts, including the Sistine Chapel',
          category: 'Museum',
          visit_duration_hours: 4,
          source_url: 'https://www.museivaticani.va/content/museivaticani/en.html',
        },
      ],
      events: [
        {
          name: 'Estate Romana',
          dates: {
            start: '2026-06-01',
            end: '2026-09-30',
          },
          description: 'Summer festival featuring concerts, film screenings, and cultural events',
          venue: 'Various venues throughout Rome',
          source_url: 'https://www.estateromana.comune.roma.it/',
        },
      ],
      weather: {
        avg_high_celsius: 28,
        avg_low_celsius: 18,
        precipitation_chance: '20%',
        clothing_suggestion: 'Summer clothes with sun protection and comfortable walking shoes',
        source_url: 'https://www.weather.com/weather/monthly/l/Rome+Italy',
      },
    },
  ],
  generated_at: '2026-05-15T14:30:00Z',
};
