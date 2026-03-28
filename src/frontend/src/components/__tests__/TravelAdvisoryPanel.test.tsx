import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TravelAdvisoryPanel } from '../TravelAdvisoryPanel/TravelAdvisoryPanel';
import {
  level1Advisory,
  level2Advisory,
  level3Advisory,
  level4Advisory,
} from '../../test/fixtures';

describe('TravelAdvisoryPanel', () => {
  describe('header rendering', () => {
    it('renders the advisory level and label for Level 1', () => {
      render(<TravelAdvisoryPanel advisory={level1Advisory} />);

      expect(
        screen.getByText(/Level 1 — Exercise Normal Precautions/i)
      ).toBeInTheDocument();
    });

    it('renders the advisory level and label for Level 2', () => {
      render(<TravelAdvisoryPanel advisory={level2Advisory} />);

      expect(
        screen.getByText(/Level 2 — Exercise Increased Caution/i)
      ).toBeInTheDocument();
    });

    it('renders the advisory level and label for Level 3', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(
        screen.getByText(/Level 3 — Reconsider Travel/i)
      ).toBeInTheDocument();
    });

    it('renders the advisory level and label for Level 4', () => {
      render(<TravelAdvisoryPanel advisory={level4Advisory} />);

      expect(
        screen.getByText(/Level 4 — Do Not Travel/i)
      ).toBeInTheDocument();
    });

    it('displays the advisory summary text', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(
        screen.getByText(level3Advisory.advisory_summary)
      ).toBeInTheDocument();
    });
  });

  describe('risk gauge', () => {
    it('renders a meter element with correct aria attributes', () => {
      render(<TravelAdvisoryPanel advisory={level2Advisory} />);

      const meter = screen.getByRole('meter', {
        name: /advisory risk level/i,
      });
      expect(meter).toBeInTheDocument();
      expect(meter).toHaveAttribute('aria-valuenow', '2');
      expect(meter).toHaveAttribute('aria-valuemin', '1');
      expect(meter).toHaveAttribute('aria-valuemax', '4');
      expect(meter).toHaveAttribute(
        'aria-valuetext',
        'Level 2: Exercise Increased Caution'
      );
    });

    it('displays all four gauge segment labels', () => {
      render(<TravelAdvisoryPanel advisory={level1Advisory} />);

      expect(screen.getByText('Normal')).toBeInTheDocument();
      expect(screen.getByText('Caution')).toBeInTheDocument();
      expect(screen.getByText('Reconsider')).toBeInTheDocument();
      expect(screen.getByText('Do Not Travel')).toBeInTheDocument();
    });

    it('shows the risk level caption', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(
        screen.getByText('Risk Level: 3 of 4')
      ).toBeInTheDocument();
    });

    it('shows correct caption for Level 1', () => {
      render(<TravelAdvisoryPanel advisory={level1Advisory} />);

      expect(
        screen.getByText('Risk Level: 1 of 4')
      ).toBeInTheDocument();
    });
  });

  describe('accessibility roles', () => {
    it('uses role="region" for Level 1 (non-severe)', () => {
      render(<TravelAdvisoryPanel advisory={level1Advisory} />);

      expect(
        screen.getByRole('region', {
          name: /Travel Advisory: Level 1/i,
        })
      ).toBeInTheDocument();
    });

    it('uses role="region" for Level 2 (non-severe)', () => {
      render(<TravelAdvisoryPanel advisory={level2Advisory} />);

      expect(
        screen.getByRole('region', {
          name: /Travel Advisory: Level 2/i,
        })
      ).toBeInTheDocument();
    });

    it('uses role="alert" for Level 3 (severe)', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(
        screen.getByRole('alert', {
          name: /Travel Advisory: Level 3/i,
        })
      ).toBeInTheDocument();
    });

    it('uses role="alert" for Level 4 (severe)', () => {
      render(<TravelAdvisoryPanel advisory={level4Advisory} />);

      expect(
        screen.getByRole('alert', {
          name: /Travel Advisory: Level 4/i,
        })
      ).toBeInTheDocument();
    });
  });

  describe('specific warnings', () => {
    it('renders all specific warnings for Level 3', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(
        screen.getByText('Specific Warnings')
      ).toBeInTheDocument();

      for (const warning of level3Advisory.specific_warnings) {
        expect(screen.getByText(warning)).toBeInTheDocument();
      }
    });

    it('renders all specific warnings for Level 4', () => {
      render(<TravelAdvisoryPanel advisory={level4Advisory} />);

      for (const warning of level4Advisory.specific_warnings) {
        expect(screen.getByText(warning)).toBeInTheDocument();
      }
    });

    it('renders warnings as list items', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      const listItems = screen.getAllByRole('listitem');
      expect(listItems).toHaveLength(
        level3Advisory.specific_warnings.length
      );
    });

    it('does not render warnings section for empty array', () => {
      render(<TravelAdvisoryPanel advisory={level1Advisory} />);

      expect(
        screen.queryByText('Specific Warnings')
      ).not.toBeInTheDocument();
    });
  });

  describe('Level 4 do-not-travel callout', () => {
    it('shows do-not-travel recommendation for Level 4', () => {
      render(<TravelAdvisoryPanel advisory={level4Advisory} />);

      expect(
        screen.getByText(
          /advises against all travel.*consider choosing an alternate/i
        )
      ).toBeInTheDocument();
    });

    it('does not show do-not-travel for Level 3', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(
        screen.queryByText(/advises against all travel/i)
      ).not.toBeInTheDocument();
    });

    it('does not show do-not-travel for Level 1', () => {
      render(<TravelAdvisoryPanel advisory={level1Advisory} />);

      expect(
        screen.queryByText(/advises against all travel/i)
      ).not.toBeInTheDocument();
    });
  });

  describe('source attribution', () => {
    it('renders source URL as a link', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      const link = screen.getByRole('link', {
        name: /view full advisory/i,
      });
      expect(link).toHaveAttribute(
        'href',
        level3Advisory.source_url
      );
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('link text includes State Department attribution', () => {
      render(<TravelAdvisoryPanel advisory={level1Advisory} />);

      expect(
        screen.getByText(/U\.S\. State Department/i)
      ).toBeInTheDocument();
    });
  });

  describe('last updated timestamp', () => {
    it('displays formatted date when last_updated is provided', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(screen.getByText(/last updated/i)).toBeInTheDocument();
      const timeEl = screen.getByRole('time');
      expect(timeEl).toHaveAttribute(
        'datetime',
        level3Advisory.last_updated!
      );
    });

    it('renders time element with semantic datetime attribute', () => {
      render(<TravelAdvisoryPanel advisory={level2Advisory} />);

      const timeEl = screen.getByRole('time');
      expect(timeEl).toHaveAttribute(
        'datetime',
        level2Advisory.last_updated!
      );
    });

    it('does not render last updated when null', () => {
      const advisoryNoDate = {
        ...level3Advisory,
        last_updated: null,
      };
      render(<TravelAdvisoryPanel advisory={advisoryNoDate} />);

      expect(
        screen.queryByText(/last updated/i)
      ).not.toBeInTheDocument();
      expect(screen.queryByRole('time')).not.toBeInTheDocument();
    });
  });

  describe('all levels render without errors', () => {
    it('Level 1 renders complete panel', () => {
      const { container } = render(
        <TravelAdvisoryPanel advisory={level1Advisory} />
      );

      expect(container.firstChild).toBeTruthy();
      expect(
        screen.getByText(/Level 1 — Exercise Normal Precautions/i)
      ).toBeInTheDocument();
      expect(
        screen.getByRole('meter')
      ).toBeInTheDocument();
      expect(
        screen.getByRole('link', { name: /view full advisory/i })
      ).toBeInTheDocument();
    });

    it('Level 2 renders complete panel', () => {
      const { container } = render(
        <TravelAdvisoryPanel advisory={level2Advisory} />
      );

      expect(container.firstChild).toBeTruthy();
      expect(
        screen.getByText(/Level 2 — Exercise Increased Caution/i)
      ).toBeInTheDocument();
    });

    it('Level 3 renders complete panel with warnings', () => {
      render(<TravelAdvisoryPanel advisory={level3Advisory} />);

      expect(
        screen.getByText(/Level 3 — Reconsider Travel/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText('Specific Warnings')
      ).toBeInTheDocument();
    });

    it('Level 4 renders complete panel with warnings and callout', () => {
      render(<TravelAdvisoryPanel advisory={level4Advisory} />);

      expect(
        screen.getByText(/Level 4 — Do Not Travel/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText('Specific Warnings')
      ).toBeInTheDocument();
      expect(
        screen.getByText(/advises against all travel/i)
      ).toBeInTheDocument();
    });
  });
});
