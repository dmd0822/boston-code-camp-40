import styles from './ErrorState.module.css';

interface ErrorStateProps {
  error: string;
  onRetry: () => void | Promise<void>;
  onReset?: () => void;
}

interface FriendlyErrorCopy {
  title: string;
  message: string;
  hint: string;
}

/**
 * Maps technical failures to user-friendly recovery guidance.
 */
function getFriendlyErrorCopy(error: string): FriendlyErrorCopy {
  const normalizedError = error.toLowerCase();

  if (
    normalizedError.includes('network')
    || normalizedError.includes('failed to fetch')
    || normalizedError.includes('fetch')
  ) {
    return {
      title: 'We could not reach the itinerary service',
      message:
        'Your trip request is ready, but the service did not respond.',
      hint: 'Please check your connection and try again in a moment.',
    };
  }

  if (normalizedError.includes('timeout') || normalizedError.includes('timed out')) {
    return {
      title: 'The itinerary is taking longer than expected',
      message:
        'Our travel specialists are still gathering recommendations.',
      hint: 'Retry to start a fresh request once the service settles down.',
    };
  }

  if (normalizedError.includes('400') || normalizedError.includes('invalid')) {
    return {
      title: 'We need a quick adjustment to your trip details',
      message:
        'A few preferences may need another look before we can build the itinerary.',
      hint: 'Go back, review the form, and submit again.',
    };
  }

  return {
    title: 'We hit a snag building your itinerary',
    message:
      'The planning workflow stopped before we could finish the results.',
    hint: 'Please retry. If it happens again, tweak your request and resubmit.',
  };
}

/**
 * Error state component.
 * Displays recovery guidance, technical details, and retry actions.
 */
export function ErrorState({ error, onRetry, onReset }: ErrorStateProps) {
  const copy = getFriendlyErrorCopy(error);

  return (
    <section
      className={styles.container}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className={styles.icon} aria-hidden="true">⚠️</div>
      <h2 className={styles.title}>{copy.title}</h2>
      <p className={styles.message}>{copy.message}</p>
      <p className={styles.hint}>{copy.hint}</p>

      <div className={styles.actions}>
        <button
          type="button"
          className={styles.retryButton}
          onClick={() => {
            void onRetry();
          }}
        >
          Retry itinerary
        </button>
        {onReset && (
          <button
            type="button"
            className={styles.secondaryButton}
            onClick={onReset}
          >
            Edit trip details
          </button>
        )}
      </div>

      <div className={styles.detailCard}>
        <span className={styles.detailLabel}>Error details</span>
        <span className={styles.detailValue}>{error}</span>
      </div>
    </section>
  );
}
