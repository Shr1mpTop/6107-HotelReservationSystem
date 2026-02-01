"use client";

import { useState, useEffect } from "react";
import { ApiService, Room } from "../lib/api";
import "./ReservationForm.css";

interface ReservationFormProps {
  onSuccess?: () => void;
}

export default function ReservationForm({ onSuccess }: ReservationFormProps) {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Form fields
  const [guestFirstName, setGuestFirstName] = useState("");
  const [guestLastName, setGuestLastName] = useState("");
  const [guestEmail, setGuestEmail] = useState("");
  const [guestPhone, setGuestPhone] = useState("");
  const [guestIdNumber, setGuestIdNumber] = useState("");
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [checkInDate, setCheckInDate] = useState("");
  const [checkOutDate, setCheckOutDate] = useState("");
  const [numberOfGuests, setNumberOfGuests] = useState(1);
  const [specialRequests, setSpecialRequests] = useState("");
  const [calculatedPrice, setCalculatedPrice] = useState<number | null>(null);

  useEffect(() => {
    loadAvailableRooms();
  }, []);

  useEffect(() => {
    if (selectedRoom && checkInDate && checkOutDate) {
      calculatePrice();
    } else {
      setCalculatedPrice(null);
    }
  }, [selectedRoom, checkInDate, checkOutDate]);

  const loadAvailableRooms = async () => {
    try {
      const data = await ApiService.getRooms();
      // Filter only clean (available) rooms
      const availableRooms = data.filter((room) => room.status === "Clean");
      setRooms(availableRooms);
    } catch (err) {
      console.error("Failed to load rooms", err);
    }
  };

  const calculatePrice = async () => {
    if (!selectedRoom || !checkInDate || !checkOutDate) return;

    try {
      const price = await ApiService.calculatePrice(
        selectedRoom.room_type_id,
        checkInDate,
        checkOutDate,
      );
      setCalculatedPrice(price);
      setError(""); // Clear any previous errors
    } catch (err: any) {
      console.error("Failed to calculate price", err);
      // Set calculated price to base price * nights as fallback
      if (checkInDate && checkOutDate) {
        const nights = Math.ceil(
          (new Date(checkOutDate).getTime() - new Date(checkInDate).getTime()) /
            (1000 * 60 * 60 * 24),
        );
        setCalculatedPrice(selectedRoom.base_price * nights);
      }
      // Don't show error to user, just use fallback calculation
    }
  };

  const validateForm = (): boolean => {
    if (!guestFirstName.trim()) {
      setError("Please enter guest first name");
      return false;
    }
    if (!guestLastName.trim()) {
      setError("Please enter guest last name");
      return false;
    }
    if (!guestEmail.trim() || !guestEmail.includes("@")) {
      setError("Please enter a valid email address");
      return false;
    }
    if (!guestPhone.trim()) {
      setError("Please enter phone number");
      return false;
    }
    if (!guestIdNumber.trim()) {
      setError("Please enter ID number");
      return false;
    }
    if (!selectedRoom) {
      setError("Please select a room");
      return false;
    }
    if (!checkInDate) {
      setError("Please select check-in date");
      return false;
    }
    if (!checkOutDate) {
      setError("Please select check-out date");
      return false;
    }
    if (new Date(checkInDate) >= new Date(checkOutDate)) {
      setError("Check-out date must be after check-in date");
      return false;
    }
    if (numberOfGuests > selectedRoom.max_occupancy) {
      setError(
        `Number of guests exceeds room capacity (max: ${selectedRoom.max_occupancy})`,
      );
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!validateForm()) return;

    setLoading(true);
    try {
      const reservationData = {
        room_id: selectedRoom!.room_id,
        guest_first_name: guestFirstName.trim(),
        guest_last_name: guestLastName.trim(),
        guest_email: guestEmail.trim(),
        guest_phone: guestPhone.trim(),
        guest_id_number: guestIdNumber.trim(),
        check_in_date: checkInDate,
        check_out_date: checkOutDate,
        number_of_guests: numberOfGuests,
        special_requests: specialRequests.trim(),
      };

      await ApiService.createReservation(reservationData);
      setSuccess("Reservation created successfully!");

      // Reset form
      resetForm();

      if (onSuccess) {
        setTimeout(() => onSuccess(), 1500);
      }
    } catch (err: any) {
      // Handle different error response formats
      let errorMessage = "Failed to create reservation";

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        // Check if detail is an array (validation errors)
        if (Array.isArray(detail)) {
          errorMessage = detail
            .map((e: any) => e.msg || e.message || String(e))
            .join(", ");
        } else if (typeof detail === "string") {
          errorMessage = detail;
        } else if (typeof detail === "object") {
          errorMessage = JSON.stringify(detail);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setGuestFirstName("");
    setGuestLastName("");
    setGuestEmail("");
    setGuestPhone("");
    setGuestIdNumber("");
    setSelectedRoom(null);
    setCheckInDate("");
    setCheckOutDate("");
    setNumberOfGuests(1);
    setSpecialRequests("");
    setCalculatedPrice(null);
  };

  const getTodayDate = () => {
    return new Date().toISOString().split("T")[0];
  };

  const getTomorrowDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split("T")[0];
  };

  return (
    <div className="reservation-form-container">
      {error && typeof error === "string" && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠</span>
          {error}
        </div>
      )}
      {success && (
        <div className="alert alert-success">
          <span className="alert-icon">✓</span>
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="reservation-form">
        {/* Guest Information Section */}
        <div className="form-section">
          <h3 className="form-section-title">
            <span className="section-icon">👤</span>
            Guest Information
          </h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstName">
                First Name <span className="required">*</span>
              </label>
              <input
                type="text"
                id="firstName"
                value={guestFirstName}
                onChange={(e) => setGuestFirstName(e.target.value)}
                placeholder="John"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="lastName">
                Last Name <span className="required">*</span>
              </label>
              <input
                type="text"
                id="lastName"
                value={guestLastName}
                onChange={(e) => setGuestLastName(e.target.value)}
                placeholder="Doe"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">
                Email <span className="required">*</span>
              </label>
              <input
                type="email"
                id="email"
                value={guestEmail}
                onChange={(e) => setGuestEmail(e.target.value)}
                placeholder="john.doe@example.com"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="phone">
                Phone <span className="required">*</span>
              </label>
              <input
                type="tel"
                id="phone"
                value={guestPhone}
                onChange={(e) => setGuestPhone(e.target.value)}
                placeholder="+1 234 567 8900"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="idNumber">
              ID Number <span className="required">*</span>
            </label>
            <input
              type="text"
              id="idNumber"
              value={guestIdNumber}
              onChange={(e) => setGuestIdNumber(e.target.value)}
              placeholder="Passport or National ID"
              required
            />
          </div>
        </div>

        {/* Room Selection Section */}
        <div className="form-section">
          <h3 className="form-section-title">
            <span className="section-icon">🏨</span>
            Room Selection
          </h3>
          <div className="room-selection-grid">
            {rooms.map((room) => (
              <div
                key={room.room_id}
                className={`room-option ${selectedRoom?.room_id === room.room_id ? "selected" : ""}`}
                onClick={() => setSelectedRoom(room)}
              >
                <div className="room-option-header">
                  <span className="room-option-number">{room.room_number}</span>
                  <span className="room-option-floor">Floor {room.floor}</span>
                </div>
                <div className="room-option-type">{room.type_name}</div>
                <div className="room-option-details">
                  <span>👥 Max {room.max_occupancy}</span>
                  <span className="room-option-price">
                    ¥{room.base_price}/night
                  </span>
                </div>
                {selectedRoom?.room_id === room.room_id && (
                  <div className="room-option-selected-badge">✓ Selected</div>
                )}
              </div>
            ))}
          </div>
          {rooms.length === 0 && (
            <p className="no-rooms-message">
              No available rooms at the moment.
            </p>
          )}
        </div>

        {/* Date and Guests Section */}
        <div className="form-section">
          <h3 className="form-section-title">
            <span className="section-icon">📅</span>
            Stay Details
          </h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="checkIn">
                Check-in Date <span className="required">*</span>
              </label>
              <input
                type="date"
                id="checkIn"
                value={checkInDate}
                onChange={(e) => setCheckInDate(e.target.value)}
                min={getTodayDate()}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="checkOut">
                Check-out Date <span className="required">*</span>
              </label>
              <input
                type="date"
                id="checkOut"
                value={checkOutDate}
                onChange={(e) => setCheckOutDate(e.target.value)}
                min={checkInDate || getTomorrowDate()}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="guests">
              Number of Guests <span className="required">*</span>
            </label>
            <input
              type="number"
              id="guests"
              value={numberOfGuests}
              onChange={(e) => setNumberOfGuests(parseInt(e.target.value) || 1)}
              min="1"
              max={selectedRoom?.max_occupancy || 10}
              required
            />
            {selectedRoom && (
              <small className="form-hint">
                Maximum capacity for this room: {selectedRoom.max_occupancy}{" "}
                guests
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="requests">Special Requests (Optional)</label>
            <textarea
              id="requests"
              value={specialRequests}
              onChange={(e) => setSpecialRequests(e.target.value)}
              placeholder="Any special requirements or requests..."
              rows={4}
            />
          </div>
        </div>

        {/* Price Summary */}
        {calculatedPrice !== null && (
          <div className="price-summary">
            <div className="price-summary-row">
              <span>Room:</span>
              <span>
                {selectedRoom?.room_number} - {selectedRoom?.type_name}
              </span>
            </div>
            <div className="price-summary-row">
              <span>Duration:</span>
              <span>
                {checkInDate && checkOutDate
                  ? Math.ceil(
                      (new Date(checkOutDate).getTime() -
                        new Date(checkInDate).getTime()) /
                        (1000 * 60 * 60 * 24),
                    )
                  : 0}{" "}
                nights
              </span>
            </div>
            <div className="price-summary-row total">
              <span>Total Price:</span>
              <span className="total-amount">
                ¥{calculatedPrice.toFixed(2)}
              </span>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="form-actions">
          <button
            type="button"
            onClick={resetForm}
            className="btn btn-secondary"
            disabled={loading}
          >
            Reset Form
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Creating Reservation..." : "Create Reservation"}
          </button>
        </div>
      </form>
    </div>
  );
}
