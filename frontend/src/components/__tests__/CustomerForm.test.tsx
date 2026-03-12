import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CustomerForm } from '../CustomerForm/CustomerForm';
import type { CustomerProfile } from '../../types/itinerary';

describe('CustomerForm', () => {
  it('should render all form fields', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    expect(screen.getByLabelText(/interests/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/budget/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/party size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/departure city/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/additional notes/i)).toBeInTheDocument();
  });

  it('should call onSubmit with correct CustomerProfile data', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    // Fill out the form
    await user.type(screen.getByLabelText(/interests/i), 'history, food, art');
    await user.selectOptions(screen.getByLabelText(/budget/i), 'luxury');
    await user.type(screen.getByLabelText(/start date/i), '2026-07-01');
    await user.type(screen.getByLabelText(/end date/i), '2026-07-15');
    await user.clear(screen.getByLabelText(/party size/i));
    await user.type(screen.getByLabelText(/party size/i), '4');
    await user.type(screen.getByLabelText(/departure city/i), 'New York');
    await user.type(screen.getByLabelText(/additional notes/i), 'Looking for family-friendly activities');

    // Submit the form
    await user.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const submittedProfile: CustomerProfile = onSubmit.mock.calls[0][0];
    
    expect(submittedProfile.interests).toEqual(['history', 'food', 'art']);
    expect(submittedProfile.budget).toBe('luxury');
    expect(submittedProfile.travel_dates.start).toBe('2026-07-01');
    expect(submittedProfile.travel_dates.end).toBe('2026-07-15');
    expect(submittedProfile.party_size).toBe(4);
    expect(submittedProfile.departure_city).toBe('New York');
    expect(submittedProfile.notes).toBe('Looking for family-friendly activities');
  });

  it('should show validation error when interests is empty', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    // Fill out other required fields
    await user.type(screen.getByLabelText(/start date/i), '2026-07-01');
    await user.type(screen.getByLabelText(/end date/i), '2026-07-15');
    await user.type(screen.getByLabelText(/departure city/i), 'Boston');

    // Try to submit without interests
    await user.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(screen.getByRole('alert')).toHaveTextContent('Please enter at least one interest');
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should show validation error when departure city is empty', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    // Fill out other required fields
    await user.type(screen.getByLabelText(/interests/i), 'beach, relaxation');
    await user.type(screen.getByLabelText(/start date/i), '2026-07-01');
    await user.type(screen.getByLabelText(/end date/i), '2026-07-15');

    // Try to submit without departure city
    await user.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(screen.getByRole('alert')).toHaveTextContent('Departure city is required');
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should have submit button text "Build My Itinerary"', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    expect(screen.getByRole('button', { name: /build my itinerary/i })).toBeInTheDocument();
  });

  it('should disable submit button when disabled prop is true', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} disabled={true} />);

    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('should have budget dropdown with Budget/Moderate/Luxury options', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    const budgetSelect = screen.getByLabelText(/budget/i) as HTMLSelectElement;
    const options = Array.from(budgetSelect.options).map(option => option.value);

    expect(options).toEqual(['budget', 'moderate', 'luxury']);
  });

  it('should have party size minimum of 1', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    const partySizeInput = screen.getByLabelText(/party size/i) as HTMLInputElement;
    expect(partySizeInput.min).toBe('1');
  });

  it('should show validation error when dates are invalid', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    // Fill out fields with invalid dates (end before start)
    await user.type(screen.getByLabelText(/interests/i), 'history');
    await user.type(screen.getByLabelText(/start date/i), '2026-07-15');
    await user.type(screen.getByLabelText(/end date/i), '2026-07-01');
    await user.type(screen.getByLabelText(/departure city/i), 'Boston');

    await user.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(screen.getByRole('alert')).toHaveTextContent('End date must be after start date');
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should convert empty notes to null', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    // Fill out required fields without notes
    await user.type(screen.getByLabelText(/interests/i), 'food');
    await user.type(screen.getByLabelText(/start date/i), '2026-07-01');
    await user.type(screen.getByLabelText(/end date/i), '2026-07-15');
    await user.type(screen.getByLabelText(/departure city/i), 'Boston');

    await user.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const submittedProfile: CustomerProfile = onSubmit.mock.calls[0][0];
    expect(submittedProfile.notes).toBeNull();
  });

  it('should trim and filter interests correctly', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    // Enter interests with extra whitespace and empty entries
    await user.type(screen.getByLabelText(/interests/i), '  history  , , food , art  ,  ');
    await user.type(screen.getByLabelText(/start date/i), '2026-07-01');
    await user.type(screen.getByLabelText(/end date/i), '2026-07-15');
    await user.type(screen.getByLabelText(/departure city/i), 'Boston');

    await user.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const submittedProfile: CustomerProfile = onSubmit.mock.calls[0][0];
    expect(submittedProfile.interests).toEqual(['history', 'food', 'art']);
  });
});
