import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorState } from '../ErrorState/ErrorState';

describe('ErrorState', () => {
  it('should render error message', () => {
    const errorMessage = 'Failed to create itinerary: Network error';
    const onRetry = vi.fn();

    render(<ErrorState error={errorMessage} onRetry={onRetry} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('should call onRetry callback when retry button is clicked', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    const errorMessage = 'Something went wrong';

    render(<ErrorState error={errorMessage} onRetry={onRetry} />);

    const retryButton = screen.getByRole('button', { name: /try again/i });
    await user.click(retryButton);

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('should render "Try Again" button text', () => {
    const onRetry = vi.fn();
    const errorMessage = 'Test error';

    render(<ErrorState error={errorMessage} onRetry={onRetry} />);

    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });

  it('should render "Something went wrong" title', () => {
    const onRetry = vi.fn();
    const errorMessage = 'Test error';

    render(<ErrorState error={errorMessage} onRetry={onRetry} />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should render error icon', () => {
    const onRetry = vi.fn();
    const errorMessage = 'Test error';

    render(<ErrorState error={errorMessage} onRetry={onRetry} />);

    expect(screen.getByText('⚠️')).toBeInTheDocument();
  });

  it('should render different error messages', () => {
    const onRetry = vi.fn();
    const errorMessage1 = 'Network connection failed';

    const { rerender } = render(<ErrorState error={errorMessage1} onRetry={onRetry} />);
    expect(screen.getByText(errorMessage1)).toBeInTheDocument();

    const errorMessage2 = 'Invalid request data';
    rerender(<ErrorState error={errorMessage2} onRetry={onRetry} />);
    expect(screen.getByText(errorMessage2)).toBeInTheDocument();
  });
});
