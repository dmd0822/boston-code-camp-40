import type { ItineraryResponse } from '../../types/itinerary';
import { DestinationCard } from '../DestinationCard/DestinationCard';
import styles from './ItineraryView.module.css';

interface ItineraryViewProps {
  itinerary: ItineraryResponse;
}

/**
 * Displays the complete itinerary with all destinations.
 * Surfaces Level 3-4 travel advisories prominently at the top.
 */
export function ItineraryView({ itinerary }: ItineraryViewProps) {
  const formattedDate = new Date(itinerary.generated_at).toLocaleString();

  const severeAdvisories = itinerary.destinations.filter(
    (d) => d.travel_advisory != null && d.travel_advisory.advisory_level >= 3
  );

  return (
    <section
      className={styles.container}
      role="region"
      aria-live="polite"
      aria-label="Generated itinerary"
    >
      <header className={styles.header}>
        <h1 className={styles.title}>Your Perfect Itinerary</h1>
        <div className={styles.meta}>
          <p className={styles.metaItem}>
            <strong>{itinerary.destinations.length}</strong>{' '}
            {itinerary.destinations.length === 1 ? 'destination' : 'destinations'} curated for you
          </p>
          <p className={styles.metaItem}>Generated on {formattedDate}</p>
        </div>
      </header>

      {severeAdvisories.length > 0 && (
        <div className={styles.advisoryBanner} role="alert">
          <h2 className={styles.advisoryBannerTitle}>
            ⚠️ Travel Advisory Warnings
          </h2>
          <p className={styles.advisoryBannerText}>
            {severeAdvisories.length === 1
              ? '1 destination in your itinerary has'
              : `${severeAdvisories.length} destinations in your itinerary have`}{' '}
            elevated travel advisories. Review the details below before
            finalizing your plans.
          </p>
          <ul className={styles.advisoryBannerList}>
            {severeAdvisories.map((dest, index) => (
              <li key={index}>
                <strong>{dest.name}, {dest.country}</strong>{' '}
                — Level {dest.travel_advisory!.advisory_level}:{' '}
                {dest.travel_advisory!.advisory_level === 4
                  ? 'Do Not Travel'
                  : 'Reconsider Travel'}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className={styles.destinations}>
        {itinerary.destinations.map((destination, index) => (
          <DestinationCard key={index} destination={destination} />
        ))}
      </div>
    </section>
  );
}
