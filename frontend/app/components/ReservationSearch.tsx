"use client";

import { useState, useEffect } from "react";
import { ApiService, ReservationDetail, formatDate } from "../lib/api";
import Toast from "./Toast";
import "../components/ReservationSearch.css";

interface ReservationSearchProps {
  onEdit?: (reservation: ReservationDetail) => void;
}

export default function ReservationSearch({ onEdit }: ReservationSearchProps) {
  const [searchCriteria, setSearchCriteria] = useState({
    guest_name: "",
    phone: "",
    reservation_id: "",
    room_number: "",
  });
  const [reservations, setReservations] = useState<ReservationDetail[]>([]);
  const [selectedReservation, setSelectedReservation] =
    useState<ReservationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({
    check_in_date: "",
    check_out_date: "",
    num_guests: "",
    special_requests: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showModal, setShowModal] = useState(false);

  // Load all reservations on mount
  useEffect(() => {
    loadAllReservations();
  }, []);

  const loadAllReservations = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await ApiService.getReservations();
      setReservations(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load reservations");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    // Check if at least one search criterion is provided
    const hasSearchCriteria = Object.values(searchCriteria).some(
      (value) => value.trim() !== "",
    );

    // If no criteria, load all reservations
    if (!hasSearchCriteria) {
      loadAllReservations();
      return;
    }

    setLoading(true);
    setError("");

    try {
      const criteria: any = {};
      if (searchCriteria.guest_name)
        criteria.guest_name = searchCriteria.guest_name;
      if (searchCriteria.phone) criteria.phone = searchCriteria.phone;
      if (searchCriteria.reservation_id)
        criteria.reservation_id = Number(searchCriteria.reservation_id);
      if (searchCriteria.room_number)
        criteria.room_number = searchCriteria.room_number;

      const data = await ApiService.searchReservations(criteria);
      setReservations(data);

      if (data.length === 0) {
        setError("No reservations found matching your criteria");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to search reservations");
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = (reservation: ReservationDetail) => {
    setSelectedReservation(reservation);
    setEditData({
      check_in_date: reservation.check_in_date,
      check_out_date: reservation.check_out_date,
      num_guests: reservation.num_guests?.toString() || "1",
      special_requests: reservation.special_requests || "",
    });
    setShowModal(true);
    setEditing(false);
  };

  const handleEdit = async () => {
    if (!selectedReservation) return;

    setLoading(true);
    setError("");

    try {
      const updatePayload: any = {};
      if (editData.check_in_date !== selectedReservation.check_in_date) {
        updatePayload.check_in_date = editData.check_in_date;
      }
      if (editData.check_out_date !== selectedReservation.check_out_date) {
        updatePayload.check_out_date = editData.check_out_date;
      }
      if (
        editData.num_guests !==
        (selectedReservation.num_guests?.toString() || "1")
      ) {
        updatePayload.num_guests = Number(editData.num_guests);
      }
      if (
        editData.special_requests !==
        (selectedReservation.special_requests || "")
      ) {
        updatePayload.special_requests = editData.special_requests;
      }

      if (Object.keys(updatePayload).length === 0) {
        setError("No changes detected");
        setLoading(false);
        return;
      }

      const result = await ApiService.updateReservation(
        selectedReservation.reservation_id,
        updatePayload,
      );

      if (result.success) {
        setSuccess("Reservation updated successfully!");
        setEditing(false);
        setShowModal(false);
        loadAllReservations(); // Refresh all reservations
      } else {
        setError(result.message || "Failed to update reservation");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update reservation");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (reservationId: number) => {
    if (!confirm("Are you sure you want to cancel this reservation?")) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await ApiService.cancelReservation(reservationId);
      if (result.success) {
        setSuccess("Reservation cancelled successfully!");
        setShowModal(false);
        loadAllReservations(); // Refresh all reservations
      } else {
        setError(result.message || "Failed to cancel reservation");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to cancel reservation");
    } finally {
      setLoading(false);
    }
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
    <div className="reservation-search">
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

      <div className="search-panel">
        <h3 className="panel-title">Search Reservations</h3>

        <div className="search-form">
          <div className="search-grid">
            <div className="form-group">
              <label>Reservation ID</label>
              <input
                type="text"
                value={searchCriteria.reservation_id}
                onChange={(e) =>
                  setSearchCriteria({
                    ...searchCriteria,
                    reservation_id: e.target.value,
                  })
                }
                placeholder="Enter reservation ID"
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label>Guest Name</label>
              <input
                type="text"
                value={searchCriteria.guest_name}
                onChange={(e) =>
                  setSearchCriteria({
                    ...searchCriteria,
                    guest_name: e.target.value,
                  })
                }
                placeholder="Enter guest name"
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label>Phone Number</label>
              <input
                type="text"
                value={searchCriteria.phone}
                onChange={(e) =>
                  setSearchCriteria({
                    ...searchCriteria,
                    phone: e.target.value,
                  })
                }
                placeholder="Enter phone number"
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label>Room Number</label>
              <input
                type="text"
                value={searchCriteria.room_number}
                onChange={(e) =>
                  setSearchCriteria({
                    ...searchCriteria,
                    room_number: e.target.value,
                  })
                }
                placeholder="Enter room number"
                className="form-control"
              />
            </div>
          </div>

          <div className="search-actions">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? "Searching..." : "Search"}
            </button>
            <button
              onClick={() => {
                setSearchCriteria({
                  guest_name: "",
                  phone: "",
                  reservation_id: "",
                  room_number: "",
                });
                loadAllReservations();
              }}
              className="btn btn-secondary"
            >
              Show All
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {reservations.length > 0 && (
        <div className="results-panel">
          <h3 className="panel-title">
            Search Results{" "}
            <span className="result-count">({reservations.length})</span>
          </h3>

          <div className="table-container">
            <table className="reservations-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Guest</th>
                  <th>Phone</th>
                  <th>Room</th>
                  <th>Check-in</th>
                  <th>Check-out</th>
                  <th>Status</th>
                  <th>Price</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reservations.map((reservation) => (
                  <tr key={reservation.reservation_id}>
                    <td>#{reservation.reservation_id}</td>
                    <td>{reservation.guest_name}</td>
                    <td>{reservation.phone}</td>
                    <td>{reservation.room_number}</td>
                    <td>
                      {formatDate(reservation.check_in_date)}
                    </td>
                    <td>
                      {formatDate(reservation.check_out_date)}
                    </td>
                    <td>
                      <span
                        className={`status-badge ${getStatusColor(reservation.status)}`}
                      >
                        {reservation.status}
                      </span>
                    </td>
                    <td className="price">¥{reservation.total_price}</td>
                    <td>
                      <button
                        onClick={() => handleViewDetail(reservation)}
                        className="btn btn-sm btn-info"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showModal && selectedReservation && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Reservation #{selectedReservation.reservation_id}</h3>
              <button
                className="modal-close"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              {!editing ? (
                <div className="detail-view">
                  <div className="detail-section">
                    <h4>Guest Information</h4>
                    <div className="detail-grid">
                      <div className="detail-item">
                        <span className="label">Name:</span>
                        <span className="value">
                          {selectedReservation.guest_name}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Phone:</span>
                        <span className="value">
                          {selectedReservation.phone}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Email:</span>
                        <span className="value">
                          {selectedReservation.email || "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="detail-section">
                    <h4>Reservation Details</h4>
                    <div className="detail-grid">
                      <div className="detail-item">
                        <span className="label">Room:</span>
                        <span className="value">
                          {selectedReservation.room_number}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Room Type:</span>
                        <span className="value">
                          {selectedReservation.room_type}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Check-in:</span>
                        <span className="value">
                          {formatDate(selectedReservation.check_in_date)}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Check-out:</span>
                        <span className="value">
                          {formatDate(selectedReservation.check_out_date)}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Guests:</span>
                        <span className="value">
                          {selectedReservation.num_guests || 1}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Status:</span>
                        <span
                          className={`status-badge ${getStatusColor(selectedReservation.status)}`}
                        >
                          {selectedReservation.status}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Total Price:</span>
                        <span className="value price">
                          ¥{selectedReservation.total_price}
                        </span>
                      </div>
                    </div>
                    {selectedReservation.special_requests && (
                      <div className="detail-item full-width">
                        <span className="label">Special Requests:</span>
                        <span className="value">
                          {selectedReservation.special_requests}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="edit-form">
                  <div className="form-group">
                    <label>Check-in Date</label>
                    <input
                      type="date"
                      value={editData.check_in_date}
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          check_in_date: e.target.value,
                        })
                      }
                      className="form-control"
                    />
                  </div>
                  <div className="form-group">
                    <label>Check-out Date</label>
                    <input
                      type="date"
                      value={editData.check_out_date}
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          check_out_date: e.target.value,
                        })
                      }
                      className="form-control"
                    />
                  </div>
                  <div className="form-group">
                    <label>Number of Guests</label>
                    <input
                      type="number"
                      value={editData.num_guests}
                      onChange={(e) =>
                        setEditData({ ...editData, num_guests: e.target.value })
                      }
                      min="1"
                      className="form-control"
                    />
                  </div>
                  <div className="form-group">
                    <label>Special Requests</label>
                    <textarea
                      value={editData.special_requests}
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          special_requests: e.target.value,
                        })
                      }
                      rows={3}
                      className="form-control"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              {!editing ? (
                <>
                  {selectedReservation.status === "Confirmed" && (
                    <>
                      <button
                        onClick={() => setEditing(true)}
                        className="btn btn-primary"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() =>
                          handleCancel(selectedReservation.reservation_id)
                        }
                        className="btn btn-danger"
                      >
                        Cancel Reservation
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => setShowModal(false)}
                    className="btn btn-secondary"
                  >
                    Close
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={handleEdit}
                    disabled={loading}
                    className="btn btn-success"
                  >
                    {loading ? "Saving..." : "Save Changes"}
                  </button>
                  <button
                    onClick={() => setEditing(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
