import { useState, FormEvent, ChangeEvent } from 'react';
import type { CustomerProfile, Budget } from '../../types/itinerary';
import styles from './CustomerForm.module.css';

interface CustomerFormProps {
  onSubmit: (profile: CustomerProfile) => void;
  disabled?: boolean;
}

interface FormErrors {
  interests?: string;
  budget?: string;
  travelDates?: string;
  partySize?: string;
  departureCity?: string;
}

/**
 * Customer profile form component.
 * Collects travel preferences and validates inputs before submission.
 */
export function CustomerForm({ onSubmit, disabled = false }: CustomerFormProps) {
  const [interestsInput, setInterestsInput] = useState('');
  const [budget, setBudget] = useState<Budget>('moderate');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [partySize, setPartySize] = useState(2);
  const [departureCity, setDepartureCity] = useState('');
  const [notes, setNotes] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Validate interests
    const interests = interestsInput.split(',').map(i => i.trim()).filter(i => i.length > 0);
    if (interests.length === 0) {
      newErrors.interests = 'Please enter at least one interest';
    }

    // Validate dates
    if (!startDate || !endDate) {
      newErrors.travelDates = 'Both start and end dates are required';
    } else if (new Date(endDate) < new Date(startDate)) {
      newErrors.travelDates = 'End date must be after start date';
    }

    // Validate party size
    if (partySize < 1) {
      newErrors.partySize = 'Party size must be at least 1';
    }

    // Validate departure city
    if (!departureCity.trim()) {
      newErrors.departureCity = 'Departure city is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const interests = interestsInput.split(',').map(i => i.trim()).filter(i => i.length > 0);

    const profile: CustomerProfile = {
      interests,
      budget,
      travel_dates: {
        start: startDate,
        end: endDate,
      },
      party_size: partySize,
      departure_city: departureCity.trim(),
      notes: notes.trim() || null,
    };

    onSubmit(profile);
  };

  const handleInterestsChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInterestsInput(e.target.value);
    if (errors.interests) {
      setErrors({ ...errors, interests: undefined });
    }
  };

  const handleStartDateChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newStartDate = e.target.value;

    setStartDate(newStartDate);
    if (newStartDate && (!endDate || endDate < newStartDate)) {
      setEndDate(newStartDate);
    }
    if (errors.travelDates) {
      setErrors({ ...errors, travelDates: undefined });
    }
  };

  const handleEndDateChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEndDate(e.target.value);
    if (errors.travelDates) {
      setErrors({ ...errors, travelDates: undefined });
    }
  };

  const handlePartySizeChange = (e: ChangeEvent<HTMLInputElement>) => {
    setPartySize(Number(e.target.value));
    if (errors.partySize) {
      setErrors({ ...errors, partySize: undefined });
    }
  };

  const handleDepartureCityChange = (e: ChangeEvent<HTMLInputElement>) => {
    setDepartureCity(e.target.value);
    if (errors.departureCity) {
      setErrors({ ...errors, departureCity: undefined });
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.formGroup}>
        <label htmlFor="interests" className={styles.label}>
          Interests *
        </label>
        <input
          id="interests"
          type="text"
          className={`${styles.input} ${errors.interests ? styles.inputError : ''}`}
          value={interestsInput}
          onChange={handleInterestsChange}
          placeholder="e.g., history, food, nature, art"
          disabled={disabled}
          aria-describedby={errors.interests ? 'interests-error' : undefined}
        />
        <p className={styles.hint}>Enter interests separated by commas</p>
        {errors.interests && (
          <p id="interests-error" className={styles.errorMessage} role="alert">
            {errors.interests}
          </p>
        )}
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="budget" className={styles.label}>
          Budget *
        </label>
        <select
          id="budget"
          className={styles.select}
          value={budget}
          onChange={(e) => setBudget(e.target.value as Budget)}
          disabled={disabled}
        >
          <option value="budget">Budget</option>
          <option value="moderate">Moderate</option>
          <option value="luxury">Luxury</option>
        </select>
      </div>

      <div className={styles.formRow}>
        <div className={styles.formGroup}>
          <label htmlFor="startDate" className={styles.label}>
            Start Date *
          </label>
          <input
            id="startDate"
            type="date"
            className={`${styles.input} ${errors.travelDates ? styles.inputError : ''}`}
            value={startDate}
            onChange={handleStartDateChange}
            disabled={disabled}
            aria-describedby={errors.travelDates ? 'dates-error' : undefined}
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="endDate" className={styles.label}>
            End Date *
          </label>
          <input
            id="endDate"
            type="date"
            min={startDate || undefined}
            className={`${styles.input} ${errors.travelDates ? styles.inputError : ''}`}
            value={endDate}
            onChange={handleEndDateChange}
            disabled={disabled}
            aria-describedby={errors.travelDates ? 'dates-error' : undefined}
          />
        </div>
      </div>
      {errors.travelDates && (
        <p id="dates-error" className={styles.errorMessage} role="alert">
          {errors.travelDates}
        </p>
      )}

      <div className={styles.formRow}>
        <div className={styles.formGroup}>
          <label htmlFor="partySize" className={styles.label}>
            Party Size *
          </label>
          <input
            id="partySize"
            type="number"
            min="1"
            className={`${styles.input} ${errors.partySize ? styles.inputError : ''}`}
            value={partySize}
            onChange={handlePartySizeChange}
            disabled={disabled}
            aria-describedby={errors.partySize ? 'partySize-error' : undefined}
          />
          {errors.partySize && (
            <p id="partySize-error" className={styles.errorMessage} role="alert">
              {errors.partySize}
            </p>
          )}
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="departureCity" className={styles.label}>
            Departure City *
          </label>
          <input
            id="departureCity"
            type="text"
            className={`${styles.input} ${errors.departureCity ? styles.inputError : ''}`}
            value={departureCity}
            onChange={handleDepartureCityChange}
            placeholder="e.g., Boston"
            disabled={disabled}
            aria-describedby={errors.departureCity ? 'departureCity-error' : undefined}
          />
          {errors.departureCity && (
            <p id="departureCity-error" className={styles.errorMessage} role="alert">
              {errors.departureCity}
            </p>
          )}
        </div>
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="notes" className={styles.label}>
          Additional Notes
        </label>
        <textarea
          id="notes"
          className={styles.textarea}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any special requests or preferences..."
          rows={4}
          disabled={disabled}
        />
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={disabled}
      >
        {disabled ? 'Building Itinerary...' : 'Build My Itinerary'}
      </button>
    </form>
  );
}
