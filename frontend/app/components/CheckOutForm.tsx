"use client";

import { useState, useEffect } from "react";
import { ApiService, ReservationDetail, formatDate } from "../lib/api";
import Toast from "./Toast";
import "../components/CheckOutForm.css";

interface CheckOutFormProps {
  onSuccess?: () => void;
}

interface CurrentGuest {
  reservation_id: number;
  guest_name: string;
  room_number: string;
  check_in_date: string;
  check_out_date: string;
  total_price: number;
}

export default function CheckOutForm({ onSuccess }: CheckOutFormProps) {
  const [reservationId, setReservationId] = useState("");
  const [reservation, setReservation] = useState<ReservationDetail | null>(
    null,
  );
  const [currentGuests, setCurrentGuests] = useState<CurrentGuest[]>([]);
  const [paymentMethod, setPaymentMethod] = useState("Cash");
  const [paymentAmount, setPaymentAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [loadingList, setLoadingList] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const paymentMethods = [
    { value: "Cash", label: "Cash" },
    { value: "CreditCard", label: "Credit Card" },
    { value: "DebitCard", label: "Debit Card" },
    { value: "OnlineTransfer", label: "Online Transfer" },
  ];

  // Load current guests on mount
  useEffect(() => {
    loadCurrentGuests();
  }, []);

  const loadCurrentGuests = async () => {
    setLoadingList(true);
    try {
      const data = await ApiService.getCurrentGuests();
      setCurrentGuests(data || []);
    } catch (err) {
      console.error("Failed to load current guests:", err);
    } finally {
      setLoadingList(false);
    }
  };

  const handleSelectReservation = (guest: CurrentGuest) => {
    setReservationId(guest.reservation_id.toString());
    // Auto-search when selecting
    searchReservation(guest.reservation_id);
  };

  const searchReservation = async (id: number) => {
    setSearching(true);
    setError("");
    setReservation(null);

    try {
      const data = await ApiService.getReservationDetail(id);
      setReservation(data);
      setPaymentAmount(data.total_price.toString());

      if (data.status !== "CheckedIn") {
        setError(`Cannot check out: Reservation status is ${data.status}`);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Reservation not found or error loading details",
      );
    } finally {
      setSearching(false);
    }
  };

  const handleSearch = async () => {
    if (!reservationId || isNaN(Number(reservationId))) {
      setError("Please enter a valid reservation ID");
      return;
    }
    searchReservation(Number(reservationId));
  };

  const handleCheckOut = async () => {
    if (!reservation) return;

    if (
      !paymentAmount ||
      isNaN(Number(paymentAmount)) ||
      Number(paymentAmount) <= 0
    ) {
      setError("Please enter a valid payment amount");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const result = await ApiService.checkOut(
        reservation.reservation_id,
        paymentMethod,
        Number(paymentAmount),
      );

      if (result.success) {
        setSuccess(result.message || "Guest checked out successfully!");
        setReservation(null);
        setReservationId("");
        setPaymentAmount("");
        setPaymentMethod("Cash");

        if (onSuccess) {
          setTimeout(() => {
            onSuccess();
          }, 2000);
        }
      } else {
        setError(result.message || "Failed to check out guest");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Failed to check out guest. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && reservationId && !searching) {
      handleSearch();
    }
  };

  const calculateChange = () => {
    if (!reservation || !paymentAmount) return 0;
    const change = Number(paymentAmount) - reservation.total_price;
    return change > 0 ? change : 0;
  };

  return (
    <div className="check-out-form">
      {error && (
        <Toast type="error" message={error} onClose={() => setError("")} />
      )}
      {success && (
        <Toast
          type="success"
          message={success}
          onClose={() => setSuccess("")}
        />
      )}

      <div className="form-card">
        <h3 className="form-title">Guest Check-out</h3>

        {/* Current Guests List */}
        <div className="pending-list-section">
          <div className="pending-list-header">
            <h4>Current Guests (Checked In)</h4>
            <button
              className="btn btn-sm btn-secondary"
              onClick={loadCurrentGuests}
              disabled={loadingList}
            >
              {loadingList ? "Loading..." : "Refresh"}
            </button>
          </div>
          {loadingList ? (
            <p className="loading-text">Loading current guests...</p>
          ) : currentGuests.length === 0 ? (
            <p className="no-data-text">No guests currently checked in</p>
          ) : (
            <div className="pending-list">
              {currentGuests.map((guest) => (
                <div
                  key={guest.reservation_id}
                  className={`pending-item ${reservationId === guest.reservation_id.toString() ? "selected" : ""}`}
                  onClick={() => handleSelectReservation(guest)}
                >
                  <span className="reservation-id">
                    #{guest.reservation_id}
                  </span>
                  <span className="guest-name">{guest.guest_name}</span>
                  <span className="room-number">Room {guest.room_number}</span>
                  <span className="price">${guest.total_price.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Search Section */}
        <div className="search-section">
          <div className="form-group">
            <label htmlFor="reservationId">Reservation ID</label>
            <div className="input-with-button">
              <input
                type="text"
                id="reservationId"
                value={reservationId}
                onChange={(e) => setReservationId(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter reservation ID"
                disabled={searching}
                className="form-control"
              />
              <button
                onClick={handleSearch}
                disabled={!reservationId || searching}
                className="btn btn-primary"
              >
                {searching ? "Searching..." : "Search"}
              </button>
            </div>
          </div>
        </div>

        {/* Reservation Details and Payment */}
        {reservation && (
          <div className="checkout-details">
            {/* Guest Information */}
            <div className="section-box">
              <div className="section-header">
                <h4>Guest Information</h4>
                <span
                  className={`status-badge ${reservation.status.toLowerCase()}`}
                >
                  {reservation.status}
                </span>
              </div>

              <div className="details-grid">
                <div className="detail-item">
                  <span className="detail-label">Reservation ID</span>
                  <span className="detail-value">
                    #{reservation.reservation_id}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Guest Name</span>
                  <span className="detail-value">{reservation.guest_name}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Phone</span>
                  <span className="detail-value">{reservation.phone}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Room Number</span>
                  <span className="detail-value">
                    {reservation.room_number}
                  </span>
                </div>
              </div>
            </div>

            {/* Stay Information */}
            <div className="section-box">
              <div className="section-header">
                <h4>Stay Information</h4>
              </div>

              <div className="details-grid">
                <div className="detail-item">
                  <span className="detail-label">Check-in Date</span>
                  <span className="detail-value">
                    {formatDate(reservation.check_in_date)}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Check-out Date</span>
                  <span className="detail-value">
                    {formatDate(reservation.check_out_date)}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Room Type</span>
                  <span className="detail-value">{reservation.room_type}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Number of Guests</span>
                  <span className="detail-value">
                    {reservation.num_guests || 1}
                  </span>
                </div>
              </div>
            </div>

            {/* Payment Section */}
            {reservation.status === "CheckedIn" && (
              <div className="section-box payment-section">
                <div className="section-header">
                  <h4>Payment Information</h4>
                </div>

                <div className="payment-summary">
                  <div className="amount-due">
                    <span className="amount-label">Amount Due</span>
                    <span className="amount-value">
                      ¥{reservation.total_price.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="paymentMethod">Payment Method</label>
                  <select
                    id="paymentMethod"
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="form-control"
                  >
                    {paymentMethods.map((method) => (
                      <option key={method.value} value={method.value}>
                        {method.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="paymentAmount">Payment Amount (¥)</label>
                  <input
                    type="number"
                    id="paymentAmount"
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(e.target.value)}
                    step="0.01"
                    min="0"
                    className="form-control"
                    placeholder="Enter payment amount"
                  />
                </div>

                {Number(paymentAmount) > 0 && (
                  <div className="payment-calculation">
                    <div className="calc-row">
                      <span>Amount Received:</span>
                      <span className="calc-value">
                        ¥{Number(paymentAmount).toFixed(2)}
                      </span>
                    </div>
                    <div className="calc-row">
                      <span>Amount Due:</span>
                      <span className="calc-value">
                        ¥{reservation.total_price.toFixed(2)}
                      </span>
                    </div>
                    <div className="calc-row total">
                      <span>Change:</span>
                      <span className="calc-value change">
                        ¥{calculateChange().toFixed(2)}
                      </span>
                    </div>
                  </div>
                )}

                <div className="action-section">
                  <p className="confirm-text">
                    Confirm check-out and payment for {reservation.guest_name}?
                  </p>
                  <button
                    onClick={handleCheckOut}
                    disabled={loading || !paymentAmount}
                    className="btn btn-success btn-large"
                  >
                    {loading ? "Processing..." : "Confirm Check-out"}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
