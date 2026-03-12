import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingState } from '../LoadingState/LoadingState';

describe('LoadingState', () => {
  it('should render "Building your itinerary..." text', () => {
    render(<LoadingState />);

    expect(screen.getByText('Building your itinerary...')).toBeInTheDocument();
  });

  it('should render spinner element', () => {
    const { container } = render(<LoadingState />);

    // The spinner has a specific class name from CSS module
    const spinner = container.querySelector('[class*="spinner"]');
    expect(spinner).toBeInTheDocument();
  });

  it('should render subtitle text', () => {
    render(<LoadingState />);

    expect(
      screen.getByText(/our ai agents are searching for the best destinations/i)
    ).toBeInTheDocument();
  });

  it('should render container with proper structure', () => {
    const { container } = render(<LoadingState />);

    const containerDiv = container.querySelector('[class*="container"]');
    expect(containerDiv).toBeInTheDocument();
    expect(containerDiv?.querySelector('[class*="spinner"]')).toBeInTheDocument();
    expect(containerDiv?.querySelector('[class*="title"]')).toBeInTheDocument();
  });
});
