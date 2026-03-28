import type { CustomerProfile, Destination, ItineraryResponse, TravelAdvisory } from '../types/itinerary';

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

export const level1Advisory: TravelAdvisory = {
  advisory_level: 1,
  advisory_summary: 'Exercise normal precautions when traveling to France.',
  specific_warnings: [],
  last_updated: '2026-01-15T00:00:00Z',
  source_url: 'https://travel.state.gov/france',
};

export const level2Advisory: TravelAdvisory = {
  advisory_level: 2,
  advisory_summary: 'Exercise increased caution due to occasional civil unrest.',
  specific_warnings: ['Avoid demonstrations and large gatherings.'],
  last_updated: '2026-02-10T00:00:00Z',
  source_url: 'https://travel.state.gov/italy',
};

export const level3Advisory: TravelAdvisory = {
  advisory_level: 3,
  advisory_summary: 'Reconsider travel due to civil unrest and crime.',
  specific_warnings: [
    'Violent crime is common in urban areas.',
    'Political demonstrations can turn violent without warning.',
  ],
  last_updated: '2026-03-01T00:00:00Z',
  source_url: 'https://travel.state.gov/test-country-3',
};

export const level4Advisory: TravelAdvisory = {
  advisory_level: 4,
  advisory_summary: 'Do not travel due to armed conflict and terrorism.',
  specific_warnings: [
    'Armed conflict is ongoing.',
    'Terrorist groups continue to plan attacks.',
    'The U.S. Embassy has limited ability to provide emergency services.',
  ],
  last_updated: '2026-03-10T00:00:00Z',
  source_url: 'https://travel.state.gov/test-country-4',
};

export const destinationWithLevel3Advisory: Destination = {
  name: 'TestCity',
  country: 'TestLand',
  rationale: 'An adventurous destination with rich cultural history.',
  points_of_interest: [],
  events: [],
  weather: null,
  travel_advisory: level3Advisory,
};

export const destinationWithLevel4Advisory: Destination = {
  name: 'DangerTown',
  country: 'RiskNation',
  rationale: 'Unique cultural experiences in a challenging environment.',
  points_of_interest: [],
  events: [],
  weather: null,
  travel_advisory: level4Advisory,
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
      travel_advisory: level1Advisory,
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
      travel_advisory: level2Advisory,
    },
  ],
  generated_at: '2026-05-15T14:30:00Z',
};
