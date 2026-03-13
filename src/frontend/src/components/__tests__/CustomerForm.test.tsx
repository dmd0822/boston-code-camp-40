import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { CustomerForm } from '../CustomerForm/CustomerForm';
import type { CustomerProfile } from '../../types/itinerary';

function setValue(label: RegExp, value: string) {
  fireEvent.change(screen.getByLabelText(label), {
    target: { value },
  });
}

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

  it('should call onSubmit with correct CustomerProfile data', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    setValue(/interests/i, 'history, food, art');
    setValue(/budget/i, 'luxury');
    setValue(/start date/i, '2026-07-01');
    setValue(/end date/i, '2026-07-15');
    setValue(/party size/i, '4');
    setValue(/departure city/i, 'New York');
    setValue(/additional notes/i, 'Looking for family-friendly activities');

    fireEvent.click(screen.getByRole('button', { name: /build my itinerary/i }));

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

  it('should show validation error when interests is empty', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    setValue(/start date/i, '2026-07-01');
    setValue(/end date/i, '2026-07-15');
    setValue(/departure city/i, 'Boston');

    fireEvent.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(
      screen.getByText('Please enter at least one interest')
    ).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should show validation error when departure city is empty', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    setValue(/interests/i, 'beach, relaxation');
    setValue(/start date/i, '2026-07-01');
    setValue(/end date/i, '2026-07-15');

    fireEvent.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(screen.getByText('Departure city is required')).toBeInTheDocument();
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
    const options = Array.from(budgetSelect.options).map((option) => option.value);

    expect(options).toEqual(['budget', 'moderate', 'luxury']);
  });

  it('should default the end date to the selected start date when empty', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    const startDateInput = screen.getByLabelText(/start date/i) as HTMLInputElement;
    const endDateInput = screen.getByLabelText(/end date/i) as HTMLInputElement;

    fireEvent.change(startDateInput, { target: { value: '2026-07-01' } });

    expect(endDateInput.value).toBe('2026-07-01');
  });

  it('should update the end date when a new start date is after the current end date', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    const startDateInput = screen.getByLabelText(/start date/i) as HTMLInputElement;
    const endDateInput = screen.getByLabelText(/end date/i) as HTMLInputElement;

    fireEvent.change(startDateInput, { target: { value: '2026-07-01' } });
    fireEvent.change(endDateInput, { target: { value: '2026-07-05' } });
    fireEvent.change(startDateInput, { target: { value: '2026-07-10' } });

    expect(endDateInput.value).toBe('2026-07-10');
  });

  it('should preserve a later end date when the start date changes', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    const startDateInput = screen.getByLabelText(/start date/i) as HTMLInputElement;
    const endDateInput = screen.getByLabelText(/end date/i) as HTMLInputElement;

    fireEvent.change(startDateInput, { target: { value: '2026-07-01' } });
    fireEvent.change(endDateInput, { target: { value: '2026-07-15' } });
    fireEvent.change(startDateInput, { target: { value: '2026-07-10' } });

    expect(endDateInput.value).toBe('2026-07-15');
  });

  it('should have party size minimum of 1', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    const partySizeInput = screen.getByLabelText(/party size/i) as HTMLInputElement;
    expect(partySizeInput.min).toBe('1');
  });

  it('should set the end date minimum to the selected start date', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    const startDateInput = screen.getByLabelText(/start date/i) as HTMLInputElement;
    const endDateInput = screen.getByLabelText(/end date/i) as HTMLInputElement;

    expect(endDateInput.min).toBe('');

    fireEvent.change(startDateInput, { target: { value: '2026-07-01' } });

    expect(endDateInput.min).toBe('2026-07-01');
  });

  it('should show validation error when dates are invalid', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    setValue(/interests/i, 'history');
    setValue(/start date/i, '2026-07-15');
    setValue(/end date/i, '2026-07-01');
    setValue(/departure city/i, 'Boston');

    const form = screen
      .getByRole('button', { name: /build my itinerary/i })
      .closest('form') as HTMLFormElement;

    fireEvent.submit(form);

    expect(screen.getByText('End date must be after start date')).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should convert empty notes to null', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    setValue(/interests/i, 'food');
    setValue(/start date/i, '2026-07-01');
    setValue(/end date/i, '2026-07-15');
    setValue(/departure city/i, 'Boston');

    fireEvent.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const submittedProfile: CustomerProfile = onSubmit.mock.calls[0][0];
    expect(submittedProfile.notes).toBeNull();
  });

  it('should trim and filter interests correctly', () => {
    const onSubmit = vi.fn();
    render(<CustomerForm onSubmit={onSubmit} />);

    setValue(/interests/i, '  history  , , food , art  ,  ');
    setValue(/start date/i, '2026-07-01');
    setValue(/end date/i, '2026-07-15');
    setValue(/departure city/i, 'Boston');

    fireEvent.click(screen.getByRole('button', { name: /build my itinerary/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const submittedProfile: CustomerProfile = onSubmit.mock.calls[0][0];
    expect(submittedProfile.interests).toEqual(['history', 'food', 'art']);
  });
});
