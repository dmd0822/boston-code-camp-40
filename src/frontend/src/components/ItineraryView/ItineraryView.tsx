import type { ItineraryResponse } from '../../types/itinerary';
import { DestinationCard } from '../DestinationCard/DestinationCard';
import styles from './ItineraryView.module.css';

interface ItineraryViewProps {
  itinerary: ItineraryResponse;
}

/**
 * Displays the complete itinerary with all destinations.
 * Renders header information and maps over destinations.
 */
export function ItineraryView({ itinerary }: ItineraryViewProps) {
  const formattedDate = new Date(itinerary.generated_at).toLocaleString();

  return (
    <div className={styles.container}>
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

      <div className={styles.destinations}>
        {itinerary.destinations.map((destination, index) => (
          <DestinationCard key={index} destination={destination} />
        ))}
      </div>
    </div>
  );
}
