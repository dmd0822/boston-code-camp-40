/**
 * TypeScript types matching the backend Pydantic models.
 * Uses snake_case to match the backend JSON responses.
 */

export type Budget = 'budget' | 'moderate' | 'luxury';

export interface TravelDates {
  start: string;  // ISO date YYYY-MM-DD
  end: string;
}

export interface CustomerProfile {
  interests: string[];
  budget: Budget;
  travel_dates: TravelDates;
  party_size: number;
  departure_city: string;
  notes?: string | null;
}

export interface PointOfInterest {
  name: string;
  description: string;
  category: string;
  visit_duration_hours: number;
  source_url?: string | null;
}

export interface EventDates {
  start: string;
  end: string;
}

export interface Event {
  name: string;
  dates: EventDates;
  description: string;
  venue: string;
  source_url?: string | null;
}

export interface WeatherForecast {
  avg_high_celsius: number;
  avg_low_celsius: number;
  precipitation_chance: string;
  clothing_suggestion: string;
  source_url?: string | null;
}

export type AdvisoryLevel = 1 | 2 | 3 | 4;

export interface TravelAdvisory {
  advisory_level: AdvisoryLevel;
  advisory_summary: string;
  specific_warnings: string[];
  last_updated: string | null;
  source_url: string;
}

export interface Destination {
  name: string;
  country: string;
  rationale: string;
  points_of_interest: PointOfInterest[];
  events: Event[];
  weather?: WeatherForecast | null;
  travel_advisory?: TravelAdvisory | null;
}

export interface ItineraryResponse {
  destinations: Destination[];
  generated_at: string;  // ISO datetime
}
