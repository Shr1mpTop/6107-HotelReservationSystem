"use client";

import { useState, useEffect } from "react";
import { ApiService, ReservationDetail } from "../lib/api";
import Toast from "./Toast";
import "../components/GuestsList.css";

interface GuestsListProps {
  type: "today-checkins" | "current-guests";
}

export default function GuestsList({ type }: GuestsListProps) {
  const [guests, setGuests] = useState<ReservationDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedGuest, setSelectedGuest] = useState<ReservationDetail | null>(
    null,
  );
  const [showModal, setShowModal] = useState(false);

  const title =
    type === "today-checkins" ? "Today's Check-ins" : "Current Guests";
  const description =
    type === "today-checkins"
      ? "Guests expected to check in today"
      : "Guests currently checked in";

  useEffect(() => {
    loadGuests();
  }, [type]);

  const loadGuests = async () => {
    setLoading(true);
    setError("");

    try {
      const data =
        type === "today-checkins"
          ? await ApiService.getTodayCheckins()
          : await ApiService.getCurrentGuests();
      setGuests(data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || `Failed to load ${title.toLowerCase()}`,
      );
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = (guest: ReservationDetail) => {
    setSelectedGuest(guest);
    setShowModal(true);
  };

  const getStatusColor = (status: string) => {
    const statusMap: Record<string, string> = {
      Confirmed: "confirmed",
      CheckedIn: "checkedin",
      CheckedOut: "checkedout",
      Cancelled: "cancelled",
    };
    return statusMap[status] || "default";
  };

  return (
    <div className="guests-list">
      {error && (
        <Toast type="error" message={error} onClose={() => setError("")} />
      )}

      <div className="list-header">
        <div>
          <h2 className="list-title">{title}</h2>
          <p className="list-description">{description}</p>
        </div>
        <button
          onClick={loadGuests}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {loading && guests.length === 0 ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading guest information...</p>
        </div>
      ) : guests.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            {type === "today-checkins" ? "📅" : "🏨"}
          </div>
          <h3>No Guests Found</h3>
          <p>
            {type === "today-checkins"
              ? "There are no guests scheduled to check in today"
              : "There are no guests currently checked in"}
          </p>
        </div>
      ) : (
        <div className="guests-grid">
          {guests.map((guest) => (
            <div key={guest.reservation_id} className="guest-card">
              <div className="card-header">
                <div className="guest-info-header">
                  <h3 className="guest-name">{guest.guest_name}</h3>
                  <span
                    className={`status-badge ${getStatusColor(guest.status)}`}
                  >
                    {guest.status}
                  </span>
                </div>
                <p className="reservation-id">#{guest.reservation_id}</p>
              </div>

              <div className="card-body">
                <div className="info-row">
                  <span className="info-label">Room</span>
                  <span className="info-value">{guest.room_number}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Phone</span>
                  <span className="info-value">{guest.phone}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Check-in</span>
                  <span className="info-value">
                    {new Date(guest.check_in_date).toLocaleDateString()}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Check-out</span>
                  <span className="info-value">
                    {new Date(guest.check_out_date).toLocaleDateString()}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Guests</span>
                  <span className="info-value">{guest.num_guests || 1}</span>
                </div>
              </div>

              <div className="card-footer">
                <button
                  onClick={() => handleViewDetail(guest)}
                  className="btn btn-info btn-sm"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {showModal && selectedGuest && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Guest Details - {selectedGuest.guest_name}</h3>
              <button
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="detail-section">
                <h4>Guest Information</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="label">Name:</span>
                    <span className="value">{selectedGuest.guest_name}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Phone:</span>
                    <span className="value">{selectedGuest.phone}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Email:</span>
                    <span className="value">
                      {selectedGuest.email || "N/A"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Reservation Details</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="label">Reservation ID:</span>
                    <span className="value">
                      #{selectedGuest.reservation_id}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Room:</span>
                    <span className="value">{selectedGuest.room_number}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Room Type:</span>
                    <span className="value">{selectedGuest.room_type}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Check-in Date:</span>
                    <span className="value">
                      {new Date(
                        selectedGuest.check_in_date,
                      ).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Check-out Date:</span>
                    <span className="value">
                      {new Date(
                        selectedGuest.check_out_date,
                      ).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Number of Guests:</span>
                    <span className="value">
                      {selectedGuest.num_guests || 1}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Total Price:</span>
                    <span className="value price">
                      ¥{selectedGuest.total_price}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Status:</span>
                    <span
                      className={`status-badge ${getStatusColor(selectedGuest.status)}`}
                    >
                      {selectedGuest.status}
                    </span>
                  </div>
                </div>
                {selectedGuest.special_requests && (
                  <div className="detail-item full-width">
                    <span className="label">Special Requests:</span>
                    <span className="value">
                      {selectedGuest.special_requests}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <button
                onClick={() => setShowModal(false)}
                className="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
