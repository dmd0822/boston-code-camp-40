import type { TravelAdvisory, AdvisoryLevel } from '../../types/itinerary';
import styles from './TravelAdvisoryBadge.module.css';

interface TravelAdvisoryBadgeProps {
  advisory: TravelAdvisory;
  /** When true, renders the full warning panel instead of just a badge. */
  expanded?: boolean;
}

interface AdvisoryMeta {
  emoji: string;
  label: string;
  className: string;
}

const ADVISORY_META: Record<AdvisoryLevel, AdvisoryMeta> = {
  1: { emoji: '🟢', label: 'Exercise Normal Precautions', className: 'level1' },
  2: { emoji: '🟡', label: 'Exercise Increased Caution', className: 'level2' },
  3: { emoji: '🟠', label: 'Reconsider Travel', className: 'level3' },
  4: { emoji: '🔴', label: 'Do Not Travel', className: 'level4' },
};

/**
 * Displays a travel advisory indicator for a destination.
 * Shows as a compact badge by default, or an expanded warning panel
 * for Level 3-4 advisories.
 */
export function TravelAdvisoryBadge({ advisory, expanded = false }: TravelAdvisoryBadgeProps) {
  const meta = ADVISORY_META[advisory.advisory_level];
  const isSevere = advisory.advisory_level >= 3;

  if (expanded && isSevere) {
    return (
      <div
        className={`${styles.warningPanel} ${styles[meta.className]}`}
        role="alert"
        aria-label={`Travel advisory level ${advisory.advisory_level}: ${meta.label}`}
      >
        <div className={styles.warningHeader}>
          <span className={styles.warningEmoji} aria-hidden="true">{meta.emoji}</span>
          <div className={styles.warningHeaderText}>
            <strong className={styles.warningLevel}>
              Level {advisory.advisory_level} — {meta.label}
            </strong>
            <p className={styles.warningSummary}>{advisory.advisory_summary}</p>
          </div>
        </div>

        {advisory.specific_warnings.length > 0 && (
          <ul className={styles.warningList}>
            {advisory.specific_warnings.map((warning, index) => (
              <li key={index} className={styles.warningItem}>{warning}</li>
            ))}
          </ul>
        )}

        {advisory.advisory_level === 4 && (
          <p className={styles.alternateAdvice}>
            ⚠️ The U.S. State Department advises against travel to this
            destination. Consider choosing an alternate location.
          </p>
        )}

        <div className={styles.warningFooter}>
          {advisory.last_updated && (
            <span className={styles.lastUpdated}>
              Updated {new Date(advisory.last_updated).toLocaleDateString()}
            </span>
          )}
          <a
            href={advisory.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.sourceLink}
          >
            View full advisory →
          </a>
        </div>
      </div>
    );
  }

  return (
    <span
      className={`${styles.badge} ${styles[meta.className]}`}
      title={`Level ${advisory.advisory_level}: ${meta.label}`}
      role="status"
      aria-label={`Travel advisory level ${advisory.advisory_level}: ${meta.label}`}
    >
      <span aria-hidden="true">{meta.emoji}</span>{' '}
      <span className={styles.badgeLabel}>Level {advisory.advisory_level}</span>
    </span>
  );
}
