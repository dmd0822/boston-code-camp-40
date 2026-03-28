import { useEffect, useState } from 'react';
import styles from './LoadingState.module.css';

type LoadingStatus = 'complete' | 'active' | 'pending';

interface LoadingStep {
  id: 'destinations' | 'poi' | 'events' | 'weather' | 'advisories' | 'itinerary';
  label: string;
  description: string;
}

interface LoadingPhase {
  liveMessage: string;
  phaseLabel: string;
  summary: string;
  progress: number;
}

const LOADING_STEPS: LoadingStep[] = [
  {
    id: 'destinations',
    label: 'Finding destinations...',
    description: 'Matching places to your interests, dates, and budget.',
  },
  {
    id: 'poi',
    label: 'Gathering points of interest...',
    description: 'Collecting standout neighborhoods, landmarks, and must-see stops.',
  },
  {
    id: 'events',
    label: 'Checking local events...',
    description: 'Looking for timely conferences, festivals, and local happenings.',
  },
  {
    id: 'weather',
    label: 'Checking weather...',
    description: 'Adding seasonal context so the itinerary feels practical.',
  },
  {
    id: 'advisories',
    label: 'Checking travel advisories...',
    description: 'Reviewing State Department travel restrictions and safety alerts.',
  },
  {
    id: 'itinerary',
    label: 'Building your itinerary...',
    description: 'Blending every detail into a polished conference-ready plan.',
  },
];

const LOADING_PHASES: LoadingPhase[] = [
  {
    liveMessage: 'Finding destinations...',
    phaseLabel: 'Phase 1 of 2',
    summary:
      'The general agent is matching destinations to your trip profile.',
    progress: 28,
  },
  {
    liveMessage: 'Gathering trip details...',
    phaseLabel: 'Phase 2 of 2',
    summary:
      'Specialist agents are gathering points of interest, events, and weather in parallel.',
    progress: 72,
  },
  {
    liveMessage: 'Building your itinerary...',
    phaseLabel: 'Finalizing',
    summary:
      'We are assembling the research into a polished itinerary you can scan at a glance.',
    progress: 96,
  },
];

/**
 * Returns the visual status for each orchestration step.
 */
function getStepStatus(stepId: LoadingStep['id'], phaseIndex: number): LoadingStatus {
  if (stepId === 'destinations') {
    return phaseIndex === 0 ? 'active' : 'complete';
  }

  if (stepId === 'itinerary') {
    return phaseIndex >= 2 ? 'active' : 'pending';
  }

  // POI, events, weather, and advisories all run concurrently in Phase 2
  if (phaseIndex === 0) {
    return 'pending';
  }

  if (phaseIndex === 1) {
    return 'active';
  }

  return 'complete';
}

interface LoadingStateProps {
  phaseDurationMs?: number;
}

/**
 * Loading state component with staged progress, animation, and skeleton preview.
 * Displays while the itinerary is being generated.
 */
export function LoadingState({ phaseDurationMs = 2400 }: LoadingStateProps) {
  const [phaseIndex, setPhaseIndex] = useState(0);
  const currentPhase = LOADING_PHASES[phaseIndex];

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setPhaseIndex((currentIndex) => {
        if (currentIndex >= LOADING_PHASES.length - 1) {
          return currentIndex;
        }

        return currentIndex + 1;
      });
    }, phaseDurationMs);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [phaseDurationMs]);

  return (
    <section
      className={styles.container}
      aria-busy="true"
      aria-labelledby="loading-title"
    >
      <div className={styles.liveRegion} aria-live="polite" aria-atomic="true">
        {currentPhase.liveMessage} {currentPhase.summary}
      </div>

      <div className={styles.panel}>
        <div className={styles.statusCard}>
          <div className={styles.badgeRow}>
            <span className={styles.phaseBadge}>{currentPhase.phaseLabel}</span>
            <span className={styles.progressValue}>{currentPhase.progress}%</span>
          </div>

          <h2 id="loading-title" className={styles.title}>
            Your itinerary is taking shape
          </h2>
          <p className={styles.subtitle}>{currentPhase.summary}</p>

          <div className={styles.animationScene} aria-hidden="true">
            <div className={styles.coreGlow}></div>
            <div className={`${styles.orbitRing} ${styles.orbitRingLarge}`}></div>
            <div className={`${styles.orbitRing} ${styles.orbitRingSmall}`}></div>
            <div className={styles.orbitMarker}></div>
            <div className={styles.flightPath}></div>
          </div>

          <div
            className={styles.progressTrack}
            role="progressbar"
            aria-label="Itinerary generation progress"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={currentPhase.progress}
            aria-valuetext={`${currentPhase.phaseLabel}: ${currentPhase.liveMessage}`}
          >
            <div
              className={styles.progressFill}
              style={{ width: `${currentPhase.progress}%` }}
            ></div>
          </div>

          <ol className={styles.stepList}>
            {LOADING_STEPS.map((step) => {
              const status = getStepStatus(step.id, phaseIndex);
              const stateLabel = status === 'complete'
                ? 'Done'
                : status === 'active'
                  ? 'In progress'
                  : 'Pending';

              return (
                <li
                  key={step.id}
                  className={`${styles.stepItem} ${styles[status]}`}
                  aria-current={status === 'active' ? 'step' : undefined}
                >
                  <span className={styles.stepIndicator} aria-hidden="true">
                    <span className={styles.stepDot}></span>
                  </span>
                  <div className={styles.stepCopy}>
                    <span className={styles.stepLabel}>{step.label}</span>
                    <span className={styles.stepDescription}>{step.description}</span>
                  </div>
                  <span className={styles.stepState}>{stateLabel}</span>
                </li>
              );
            })}
          </ol>
        </div>

        <section className={styles.previewCard} aria-hidden="true">
          <p className={styles.previewEyebrow}>Preview</p>
          <h3 className={styles.previewTitle}>Your itinerary preview</h3>
          <p className={styles.previewSubtitle}>
            We are preparing a polished destination summary while the
            agents finish their research.
          </p>

          <div className={styles.previewHeader}>
            <div className={`${styles.skeletonBlock} ${styles.skeletonTitle}`}></div>
            <div className={`${styles.skeletonBlock} ${styles.skeletonMeta}`}></div>
          </div>

          {[0, 1].map((cardIndex) => (
            <article key={cardIndex} className={styles.skeletonCard}>
              <div className={styles.skeletonCardHeader}>
                <div className={`${styles.skeletonBlock} ${styles.skeletonDestination}`}></div>
                <div className={styles.skeletonPill}></div>
              </div>
              <div className={`${styles.skeletonBlock} ${styles.skeletonLineLong}`}></div>
              <div className={`${styles.skeletonBlock} ${styles.skeletonLineMedium}`}></div>
              <div className={styles.skeletonMetrics}>
                <div className={`${styles.skeletonBlock} ${styles.skeletonMetric}`}></div>
                <div className={`${styles.skeletonBlock} ${styles.skeletonMetric}`}></div>
                <div className={`${styles.skeletonBlock} ${styles.skeletonMetric}`}></div>
              </div>
            </article>
          ))}
        </section>
      </div>
    </section>
  );
}
