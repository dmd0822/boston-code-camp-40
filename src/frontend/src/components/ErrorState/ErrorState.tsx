import styles from './ErrorState.module.css';

interface ErrorStateProps {
  error: string;
  onRetry: () => void;
}

/**
 * Error state component.
 * Displays error message and retry button.
 */
export function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <div className={styles.container}>
      <div className={styles.icon}>⚠️</div>
      <h2 className={styles.title}>Something went wrong</h2>
      <p className={styles.message}>{error}</p>
      <button className={styles.retryButton} onClick={onRetry}>
        Try Again
      </button>
    </div>
  );
}
