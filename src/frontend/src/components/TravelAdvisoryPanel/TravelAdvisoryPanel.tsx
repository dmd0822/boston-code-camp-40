import type { TravelAdvisory, AdvisoryLevel } from '../../types/itinerary';
import styles from './TravelAdvisoryPanel.module.css';

interface TravelAdvisoryPanelProps {
  advisory: TravelAdvisory;
}

interface LevelMeta {
  label: string;
  shortLabel: string;
  icon: string;
  className: string;
}

const LEVEL_META: Record<AdvisoryLevel, LevelMeta> = {
  1: {
    label: 'Exercise Normal Precautions',
    shortLabel: 'Normal',
    icon: '✅',
    className: 'level1',
  },
  2: {
    label: 'Exercise Increased Caution',
    shortLabel: 'Caution',
    icon: '⚠️',
    className: 'level2',
  },
  3: {
    label: 'Reconsider Travel',
    shortLabel: 'Reconsider',
    icon: '🚨',
    className: 'level3',
  },
  4: {
    label: 'Do Not Travel',
    shortLabel: 'Do Not Travel',
    icon: '🛑',
    className: 'level4',
  },
};

/**
 * Renders a segment label for the risk gauge at each level.
 * Highlights the active level with a visual indicator.
 */
function GaugeSegment({
  level,
  activeLevel,
}: {
  level: AdvisoryLevel;
  activeLevel: AdvisoryLevel;
}) {
  const meta = LEVEL_META[level];
  const isActive = level === activeLevel;
  const isFilled = level <= activeLevel;

  return (
    <div
      className={[
        styles.gaugeSegment,
        styles[meta.className],
        isFilled ? styles.filled : '',
        isActive ? styles.active : '',
      ]
        .filter(Boolean)
        .join(' ')}
      aria-hidden="true"
    >
      <span className={styles.segmentLabel}>{meta.shortLabel}</span>
    </div>
  );
}

/**
 * Rich travel advisory panel with visual risk gauge.
 *
 * Displays the full advisory detail including a four-segment
 * risk meter, summary, specific warnings with icons, source
 * attribution, and last-updated timestamp.
 */
export function TravelAdvisoryPanel({
  advisory,
}: TravelAdvisoryPanelProps) {
  const meta = LEVEL_META[advisory.advisory_level];
  const isSevere = advisory.advisory_level >= 3;

  return (
    <section
      className={`${styles.panel} ${styles[meta.className]}`}
      role={isSevere ? 'alert' : 'region'}
      aria-label={`Travel Advisory: Level ${advisory.advisory_level} — ${meta.label}`}
    >
      {/* Header */}
      <div className={styles.header}>
        <span className={styles.headerIcon} aria-hidden="true">
          {meta.icon}
        </span>
        <div className={styles.headerText}>
          <h3 className={styles.levelTitle}>
            Level {advisory.advisory_level} — {meta.label}
          </h3>
          <p className={styles.summary}>{advisory.advisory_summary}</p>
        </div>
      </div>

      {/* Risk Gauge */}
      <div
        className={styles.gaugeContainer}
        role="meter"
        aria-label="Advisory risk level"
        aria-valuemin={1}
        aria-valuemax={4}
        aria-valuenow={advisory.advisory_level}
        aria-valuetext={`Level ${advisory.advisory_level}: ${meta.label}`}
      >
        <div className={styles.gaugeTrack}>
          {([1, 2, 3, 4] as AdvisoryLevel[]).map((level) => (
            <GaugeSegment
              key={level}
              level={level}
              activeLevel={advisory.advisory_level}
            />
          ))}
        </div>
        <div className={styles.gaugeCaption}>
          Risk Level: {advisory.advisory_level} of 4
        </div>
      </div>

      {/* Specific Warnings */}
      {advisory.specific_warnings.length > 0 && (
        <div className={styles.warningsSection}>
          <h4 className={styles.warningsTitle}>Specific Warnings</h4>
          <ul className={styles.warningsList}>
            {advisory.specific_warnings.map((warning, index) => (
              <li key={index} className={styles.warningItem}>
                <span
                  className={styles.warningIcon}
                  aria-hidden="true"
                >
                  ⚠️
                </span>
                <span>{warning}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Level 4 strong recommendation */}
      {advisory.advisory_level === 4 && (
        <div className={styles.doNotTravel}>
          <span aria-hidden="true">🛑</span>
          <p>
            The U.S. State Department advises against all travel to
            this destination. Consider choosing an alternate location.
          </p>
        </div>
      )}

      {/* Footer: source + last updated */}
      <div className={styles.footer}>
        {advisory.last_updated && (
          <span className={styles.lastUpdated}>
            Last updated:{' '}
            <time dateTime={advisory.last_updated}>
              {new Date(advisory.last_updated).toLocaleDateString(
                undefined,
                { year: 'numeric', month: 'long', day: 'numeric' }
              )}
            </time>
          </span>
        )}
        <a
          href={advisory.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.sourceLink}
        >
          U.S. State Department — View full advisory ↗
        </a>
      </div>
    </section>
  );
}
