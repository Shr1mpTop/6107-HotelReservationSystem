"use client";

import { useState, useEffect } from "react";
import { ApiService, ReservationDetail } from "../lib/api";
import Toast from "./Toast";
import "../components/CheckInForm.css";

interface CheckInFormProps {
  onSuccess?: () => void;
}

interface PendingCheckIn {
  reservation_id: number;
  guest_name: string;
  room_number: string;
  check_in_date: string;
  check_out_date: string;
}

export default function CheckInForm({ onSuccess }: CheckInFormProps) {
  const [reservationId, setReservationId] = useState("");
  const [reservation, setReservation] = useState<ReservationDetail | null>(
    null,
  );
  const [pendingCheckins, setPendingCheckins] = useState<PendingCheckIn[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [loadingList, setLoadingList] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Load pending check-ins on mount
  useEffect(() => {
    loadPendingCheckins();
  }, []);

  const loadPendingCheckins = async () => {
    setLoadingList(true);
    try {
      const data = await ApiService.getTodayCheckins();
      setPendingCheckins(data || []);
    } catch (err) {
      console.error("Failed to load pending check-ins:", err);
    } finally {
      setLoadingList(false);
    }
  };

  const handleSelectReservation = (id: number) => {
    setReservationId(id.toString());
    // Auto-search when selecting
    searchReservation(id);
  };

  const searchReservation = async (id: number) => {
    setSearching(true);
    setError("");
    setReservation(null);

    try {
      const data = await ApiService.getReservationDetail(id);
      setReservation(data);

      // Validate reservation status
      if (data.status !== "Confirmed") {
        setError(`Cannot check in: Reservation status is ${data.status}`);
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

  const handleCheckIn = async () => {
    if (!reservation) return;

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const result = await ApiService.checkIn(reservation.reservation_id);

      if (result.success) {
        setSuccess(result.message || "Guest checked in successfully!");
        setReservation(null);
        setReservationId("");

        if (onSuccess) {
          setTimeout(() => {
            onSuccess();
          }, 2000);
        }
      } else {
        setError(result.message || "Failed to check in guest");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Failed to check in guest. Please try again.",
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

  return (
    <div className="check-in-form">
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
        <h3 className="form-title">Guest Check-in</h3>

        {/* Pending Check-ins List */}
        <div className="pending-list-section">
          <div className="pending-list-header">
            <h4>Today's Pending Check-ins</h4>
            <button
              className="btn btn-sm btn-secondary"
              onClick={loadPendingCheckins}
              disabled={loadingList}
            >
              {loadingList ? "Loading..." : "Refresh"}
            </button>
          </div>
          {loadingList ? (
            <p className="loading-text">Loading pending check-ins...</p>
          ) : pendingCheckins.length === 0 ? (
            <p className="no-data-text">No pending check-ins for today</p>
          ) : (
            <div className="pending-list">
              {pendingCheckins.map((item) => (
                <div
                  key={item.reservation_id}
                  className={`pending-item ${reservationId === item.reservation_id.toString() ? "selected" : ""}`}
                  onClick={() => handleSelectReservation(item.reservation_id)}
                >
                  <span className="reservation-id">#{item.reservation_id}</span>
                  <span className="guest-name">{item.guest_name}</span>
                  <span className="room-number">Room {item.room_number}</span>
                  <span className="dates">
                    {item.check_in_date} - {item.check_out_date}
                  </span>
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

        {/* Reservation Details */}
        {reservation && (
          <div className="reservation-details">
            <div className="details-header">
              <h4>Reservation Details</h4>
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
                <span className="detail-label">Email</span>
                <span className="detail-value">
                  {reservation.email || "N/A"}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Room Number</span>
                <span className="detail-value">{reservation.room_number}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Room Type</span>
                <span className="detail-value">{reservation.room_type}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Check-in Date</span>
                <span className="detail-value">
                  {new Date(reservation.check_in_date).toLocaleDateString()}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Check-out Date</span>
                <span className="detail-value">
                  {new Date(reservation.check_out_date).toLocaleDateString()}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Number of Guests</span>
                <span className="detail-value">
                  {reservation.num_guests || 1}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Total Price</span>
                <span className="detail-value price">
                  ¥{reservation.total_price}
                </span>
              </div>
              {reservation.special_requests && (
                <div className="detail-item full-width">
                  <span className="detail-label">Special Requests</span>
                  <span className="detail-value">
                    {reservation.special_requests}
                  </span>
                </div>
              )}
            </div>

            {reservation.status === "Confirmed" && (
              <div className="action-section">
                <p className="confirm-text">
                  Confirm check-in for {reservation.guest_name}?
                </p>
                <button
                  onClick={handleCheckIn}
                  disabled={loading}
                  className="btn btn-success btn-large"
                >
                  {loading ? "Checking in..." : "Confirm Check-in"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
