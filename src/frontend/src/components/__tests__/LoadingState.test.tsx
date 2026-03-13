import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LoadingState } from '../LoadingState/LoadingState';

describe('LoadingState', () => {
  it('renders staged progress and the itinerary skeleton preview', () => {
    render(<LoadingState />);

    expect(screen.getByText('Your itinerary is taking shape')).toBeInTheDocument();
    expect(screen.getByText('Finding destinations...')).toBeInTheDocument();
    expect(screen.getByText('Gathering points of interest...')).toBeInTheDocument();
    expect(screen.getByText('Checking weather...')).toBeInTheDocument();
    expect(
      screen.getByRole('progressbar', {
        name: /itinerary generation progress/i,
      })
    ).toBeInTheDocument();
    expect(screen.getByText('Your itinerary preview')).toBeInTheDocument();
  });

  it('advances the orchestration summary as loading continues', async () => {
    render(<LoadingState phaseDurationMs={250} />);

    expect(screen.getByText(/phase 1 of 2/i)).toBeInTheDocument();

    expect(
      await screen.findByText(/phase 2 of 2/i, {}, { timeout: 600 })
    ).toBeInTheDocument();

    expect(
      await screen.findByText('Finalizing', {}, { timeout: 900 })
    ).toBeInTheDocument();
  });
});
