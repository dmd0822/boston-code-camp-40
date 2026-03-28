import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TravelAdvisoryBadge } from '../TravelAdvisoryBadge/TravelAdvisoryBadge';
import {
  level1Advisory,
  level2Advisory,
  level3Advisory,
  level4Advisory,
} from '../../test/fixtures';

describe('TravelAdvisoryBadge', () => {
  describe('compact badge (default)', () => {
    it('renders Level 1 badge with green indicator', () => {
      render(<TravelAdvisoryBadge advisory={level1Advisory} />);

      expect(screen.getByText('Level 1')).toBeInTheDocument();
      expect(screen.getByText('🟢')).toBeInTheDocument();
      expect(
        screen.getByRole('status', {
          name: /level 1.*exercise normal precautions/i,
        })
      ).toBeInTheDocument();
    });

    it('renders Level 2 badge with yellow indicator', () => {
      render(<TravelAdvisoryBadge advisory={level2Advisory} />);

      expect(screen.getByText('Level 2')).toBeInTheDocument();
      expect(screen.getByText('🟡')).toBeInTheDocument();
    });

    it('renders Level 3 badge with orange indicator', () => {
      render(<TravelAdvisoryBadge advisory={level3Advisory} />);

      expect(screen.getByText('Level 3')).toBeInTheDocument();
      expect(screen.getByText('🟠')).toBeInTheDocument();
    });

    it('renders Level 4 badge with red indicator', () => {
      render(<TravelAdvisoryBadge advisory={level4Advisory} />);

      expect(screen.getByText('Level 4')).toBeInTheDocument();
      expect(screen.getByText('🔴')).toBeInTheDocument();
    });

    it('does not render expanded content for Level 3 in default mode', () => {
      render(<TravelAdvisoryBadge advisory={level3Advisory} />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(
        screen.queryByText(level3Advisory.advisory_summary)
      ).not.toBeInTheDocument();
    });
  });

  describe('expanded warning panel', () => {
    it('renders expanded panel for Level 3 advisory', () => {
      render(<TravelAdvisoryBadge advisory={level3Advisory} expanded />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(
        screen.getByText(/level 3 — reconsider travel/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(level3Advisory.advisory_summary)
      ).toBeInTheDocument();
    });

    it('renders expanded panel for Level 4 with alternate destination advice', () => {
      render(<TravelAdvisoryBadge advisory={level4Advisory} expanded />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(
        screen.getByText(/level 4 — do not travel/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/consider choosing an alternate location/i)
      ).toBeInTheDocument();
    });

    it('renders specific warnings as a list', () => {
      render(<TravelAdvisoryBadge advisory={level3Advisory} expanded />);

      for (const warning of level3Advisory.specific_warnings) {
        expect(screen.getByText(warning)).toBeInTheDocument();
      }
    });

    it('renders source URL link', () => {
      render(<TravelAdvisoryBadge advisory={level3Advisory} expanded />);

      const link = screen.getByRole('link', { name: /view full advisory/i });
      expect(link).toHaveAttribute('href', level3Advisory.source_url);
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('renders last updated date when available', () => {
      render(<TravelAdvisoryBadge advisory={level3Advisory} expanded />);

      expect(screen.getByText(/updated/i)).toBeInTheDocument();
    });

    it('does not render last updated when null', () => {
      const advisoryNoDate = { ...level3Advisory, last_updated: null };
      render(<TravelAdvisoryBadge advisory={advisoryNoDate} expanded />);

      expect(screen.queryByText(/updated/i)).not.toBeInTheDocument();
    });

    it('falls back to compact badge for Level 1 even when expanded=true', () => {
      render(<TravelAdvisoryBadge advisory={level1Advisory} expanded />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('falls back to compact badge for Level 2 even when expanded=true', () => {
      render(<TravelAdvisoryBadge advisory={level2Advisory} expanded />);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('renders all specific warnings for Level 4', () => {
      render(<TravelAdvisoryBadge advisory={level4Advisory} expanded />);

      for (const warning of level4Advisory.specific_warnings) {
        expect(screen.getByText(warning)).toBeInTheDocument();
      }
    });
  });
});
