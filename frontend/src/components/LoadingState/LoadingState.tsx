import styles from './LoadingState.module.css';

/**
 * Loading state component with CSS spinner animation.
 * Displays while the itinerary is being generated.
 */
export function LoadingState() {
  return (
    <div className={styles.container}>
      <div className={styles.spinner}></div>
      <h2 className={styles.title}>Building your itinerary...</h2>
      <p className={styles.subtitle}>
        Our AI agents are searching for the best destinations, points of interest, events, and weather forecasts.
      </p>
    </div>
  );
}
