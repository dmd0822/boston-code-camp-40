import type { Destination } from '../../types/itinerary';
import { TravelAdvisoryBadge } from '../TravelAdvisoryBadge/TravelAdvisoryBadge';
import { TravelAdvisoryPanel } from '../TravelAdvisoryPanel/TravelAdvisoryPanel';
import styles from './DestinationCard.module.css';

interface DestinationCardProps {
  destination: Destination;
}

/**
 * Displays detailed information about a single destination.
 * Includes POIs, events, weather forecast, and travel advisory.
 */
export function DestinationCard({ destination }: DestinationCardProps) {
  const advisory = destination.travel_advisory;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h2 className={styles.title}>
          {destination.name}, {destination.country}
          {advisory && (
            <TravelAdvisoryBadge advisory={advisory} />
          )}
        </h2>
      </div>

      {/* Rich advisory panel for all levels */}
      {advisory && (
        <TravelAdvisoryPanel advisory={advisory} />
      )}

      <p className={styles.rationale}>{destination.rationale}</p>

      {/* Points of Interest */}
      {destination.points_of_interest.length > 0 && (
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>🗺️ Points of Interest</h3>
          <div className={styles.poiList}>
            {destination.points_of_interest.map((poi, index) => (
              <div key={index} className={styles.poiItem}>
                <div className={styles.poiHeader}>
                  <h4 className={styles.poiName}>{poi.name}</h4>
                  <span className={styles.categoryBadge}>{poi.category}</span>
                </div>
                <p className={styles.poiDescription}>{poi.description}</p>
                <div className={styles.poiMeta}>
                  <span className={styles.duration}>
                    ⏱️ {poi.visit_duration_hours} {poi.visit_duration_hours === 1 ? 'hour' : 'hours'}
                  </span>
                  {poi.source_url && (
                    <a
                      href={poi.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.sourceLink}
                    >
                      Learn more →
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Events */}
      {destination.events.length > 0 && (
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>🎉 Events</h3>
          <div className={styles.eventList}>
            {destination.events.map((event, index) => (
              <div key={index} className={styles.eventItem}>
                <h4 className={styles.eventName}>{event.name}</h4>
                <p className={styles.eventDates}>
                  📅 {new Date(event.dates.start).toLocaleDateString()} -{' '}
                  {new Date(event.dates.end).toLocaleDateString()}
                </p>
                <p className={styles.eventVenue}>📍 {event.venue}</p>
                <p className={styles.eventDescription}>{event.description}</p>
                {event.source_url && (
                  <a
                    href={event.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.sourceLink}
                  >
                    Event details →
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Weather */}
      {destination.weather && (
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>🌤️ Weather Forecast</h3>
          <div className={styles.weatherCard}>
            <div className={styles.weatherTemps}>
              <div className={styles.tempItem}>
                <span className={styles.tempLabel}>High</span>
                <span className={styles.tempValue}>
                  {destination.weather.avg_high_celsius}°C
                </span>
              </div>
              <div className={styles.tempItem}>
                <span className={styles.tempLabel}>Low</span>
                <span className={styles.tempValue}>
                  {destination.weather.avg_low_celsius}°C
                </span>
              </div>
            </div>
            <div className={styles.weatherInfo}>
              <p className={styles.weatherItem}>
                <strong>Precipitation:</strong> {destination.weather.precipitation_chance}
              </p>
              <p className={styles.weatherItem}>
                <strong>Clothing suggestion:</strong> {destination.weather.clothing_suggestion}
              </p>
              {destination.weather.source_url && (
                <a
                  href={destination.weather.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.sourceLink}
                >
                  Detailed forecast →
                </a>
              )}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
