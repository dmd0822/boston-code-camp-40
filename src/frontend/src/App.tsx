import { useItinerary } from './hooks/useItinerary';
import { CustomerForm } from './components/CustomerForm/CustomerForm';
import { LoadingState } from './components/LoadingState/LoadingState';
import { ErrorState } from './components/ErrorState/ErrorState';
import { ItineraryView } from './components/ItineraryView/ItineraryView';
import styles from './App.module.css';

/**
 * Main application component.
 * Manages state-based view rendering for the travel agent workflow.
 */
function App() {
  const {
    state,
    itinerary,
    error,
    submitProfile,
    retryLastSubmission,
    reset,
  } = useItinerary();

  return (
    <div className={styles.app}>
      <header className={styles.appHeader}>
        <h1 className={styles.appTitle}>✈️ Travel Agent AI</h1>
        <p className={styles.appSubtitle}>
          Discover your perfect destinations with AI-powered recommendations
        </p>
      </header>

      <main className={styles.main}>
        {state === 'idle' && (
          <div className={styles.formSection}>
            <h2 className={styles.sectionTitle}>Plan Your Trip</h2>
            <CustomerForm onSubmit={submitProfile} disabled={false} />
          </div>
        )}

        {state === 'loading' && <LoadingState />}

        {state === 'success' && itinerary && (
          <>
            <ItineraryView itinerary={itinerary} />
            <div className={styles.actionSection}>
              <button className={styles.resetButton} onClick={reset}>
                ← Plan Another Trip
              </button>
            </div>
          </>
        )}

        {state === 'error' && error && (
          <ErrorState
            error={error}
            onRetry={retryLastSubmission}
            onReset={reset}
          />
        )}
      </main>

      <footer className={styles.footer}>
        <p>Powered by AI • Built with React & TypeScript</p>
      </footer>
    </div>
  );
}

export default App;
