import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ErrorState } from '../ErrorState/ErrorState';

describe('ErrorState', () => {
  it('renders friendly network guidance and technical details', () => {
    const errorMessage = 'Failed to create itinerary: Network error';
    const onRetry = vi.fn();

    render(<ErrorState error={errorMessage} onRetry={onRetry} />);

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(
      screen.getByText('We could not reach the itinerary service')
    ).toBeInTheDocument();
    expect(
      screen.getByText(/your trip request is ready, but the service did not respond/i)
    ).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('calls onRetry when the retry button is clicked', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();

    render(<ErrorState error="Something went wrong" onRetry={onRetry} />);

    await user.click(
      screen.getByRole('button', { name: /retry itinerary/i })
    );

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('renders a reset button when provided', () => {
    const onRetry = vi.fn();
    const onReset = vi.fn();

    render(
      <ErrorState
        error="Invalid request data"
        onRetry={onRetry}
        onReset={onReset}
      />
    );

    expect(
      screen.getByRole('button', { name: /edit trip details/i })
    ).toBeInTheDocument();
  });

  it('uses the fallback copy for unexpected failures', () => {
    const onRetry = vi.fn();

    render(<ErrorState error="Unexpected failure" onRetry={onRetry} />);

    expect(
      screen.getByText('We hit a snag building your itinerary')
    ).toBeInTheDocument();
  });
});
