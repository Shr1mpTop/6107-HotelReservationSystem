"use client";

import { useState, useEffect } from "react";
import { ApiService, RoomType, SeasonalPricing, Room, formatDate } from "../lib/api";
import Toast from "./Toast";
import "../components/RoomManagement.css";

interface RoomManagementProps {
  defaultTab?: "rooms" | "room-types" | "seasonal-pricing";
}

export default function RoomManagement({
  defaultTab = "room-types",
}: RoomManagementProps) {
  const [activeTab, setActiveTab] = useState<"rooms" | "room-types" | "seasonal-pricing">(
    defaultTab,
  );
  const [rooms, setRooms] = useState<Room[]>([]);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [seasonalPricing, setSeasonalPricing] = useState<SeasonalPricing[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Room Type Form
  const [showRoomTypeForm, setShowRoomTypeForm] = useState(false);
  const [editingRoomType, setEditingRoomType] = useState<RoomType | null>(null);
  const [roomTypeForm, setRoomTypeForm] = useState({
    type_name: "",
    description: "",
    base_price: "",
    max_occupancy: "",
    amenities: "",
  });

  // Seasonal Pricing Form
  const [showPricingForm, setShowPricingForm] = useState(false);
  const [pricingForm, setPricingForm] = useState({
    room_type_id: "",
    season_name: "",
    start_date: "",
    end_date: "",
    pricing_type: "multiplier",
    price_multiplier: "",
    fixed_price: "",
  });

  useEffect(() => {
    if (activeTab === "rooms") {
      loadRooms();
      loadRoomTypes(); // Also load room types for filter
    } else if (activeTab === "room-types") {
      loadRoomTypes();
    } else {
      loadSeasonalPricing();
    }
  }, [activeTab]);

  const loadRooms = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getRoomsWithReservations();
      setRooms(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load rooms");
    } finally {
      setLoading(false);
    }
  };

  const loadRoomTypes = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getRoomTypes();
      setRoomTypes(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load room types");
    } finally {
      setLoading(false);
    }
  };

  const loadSeasonalPricing = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getSeasonalPricing();
      setSeasonalPricing(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load seasonal pricing");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRoomStatus = async (roomId: number, newStatus: string) => {
    if (!confirm(`Are you sure you want to change room status to ${newStatus}?`)) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await ApiService.updateRoomStatus(roomId, newStatus);
      if (result.success) {
        setSuccess(`Room status updated to ${newStatus}`);
        loadRooms();
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update room status");
    } finally {
      setLoading(false);
    }
  };

  // Room Type Handlers
  const handleAddRoomType = () => {
    setEditingRoomType(null);
    setRoomTypeForm({
      type_name: "",
      description: "",
      base_price: "",
      max_occupancy: "",
      amenities: "",
    });
    setShowRoomTypeForm(true);
  };

  const handleEditRoomType = (roomType: RoomType) => {
    setEditingRoomType(roomType);
    setRoomTypeForm({
      type_name: roomType.type_name,
      description: roomType.description,
      base_price: roomType.base_price.toString(),
      max_occupancy: roomType.max_occupancy.toString(),
      amenities: roomType.amenities,
    });
    setShowRoomTypeForm(true);
  };

  const handleSaveRoomType = async () => {
    if (
      !roomTypeForm.type_name ||
      !roomTypeForm.base_price ||
      !roomTypeForm.max_occupancy
    ) {
      setError("Please fill in all required fields");
      return;
    }

    setLoading(true);
    setError("");

    try {
      if (editingRoomType) {
        // Update
        const result = await ApiService.updateRoomType(
          editingRoomType.room_type_id,
          {
            type_name: roomTypeForm.type_name,
            description: roomTypeForm.description,
            base_price: Number(roomTypeForm.base_price),
            max_occupancy: Number(roomTypeForm.max_occupancy),
            amenities: roomTypeForm.amenities,
          },
        );
        if (result.success) {
          setSuccess("Room type updated successfully!");
          setShowRoomTypeForm(false);
          loadRoomTypes();
        } else {
          setError(result.message);
        }
      } else {
        // Add new
        const result = await ApiService.addRoomType({
          type_name: roomTypeForm.type_name,
          description: roomTypeForm.description,
          base_price: Number(roomTypeForm.base_price),
          max_occupancy: Number(roomTypeForm.max_occupancy),
          amenities: roomTypeForm.amenities,
        });
        if (result.success) {
          setSuccess("Room type added successfully!");
          setShowRoomTypeForm(false);
          loadRoomTypes();
        } else {
          setError(result.message);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Operation failed");
    } finally {
      setLoading(false);
    }
  };

  // Seasonal Pricing Handlers
  const handleAddPricing = () => {
    setPricingForm({
      room_type_id: "",
      season_name: "",
      start_date: "",
      end_date: "",
      pricing_type: "multiplier",
      price_multiplier: "",
      fixed_price: "",
    });
    setShowPricingForm(true);
  };

  const handleSavePricing = async () => {
    if (
      !pricingForm.room_type_id ||
      !pricingForm.season_name ||
      !pricingForm.start_date ||
      !pricingForm.end_date
    ) {
      setError("Please fill in all required fields");
      return;
    }

    if (
      pricingForm.pricing_type === "multiplier" &&
      !pricingForm.price_multiplier
    ) {
      setError("Please enter price multiplier");
      return;
    }

    if (pricingForm.pricing_type === "fixed" && !pricingForm.fixed_price) {
      setError("Please enter fixed price");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await ApiService.addSeasonalPricing({
        room_type_id: Number(pricingForm.room_type_id),
        season_name: pricingForm.season_name,
        start_date: pricingForm.start_date,
        end_date: pricingForm.end_date,
        price_multiplier:
          pricingForm.pricing_type === "multiplier"
            ? Number(pricingForm.price_multiplier)
            : undefined,
        fixed_price:
          pricingForm.pricing_type === "fixed"
            ? Number(pricingForm.fixed_price)
            : undefined,
      });

      if (result.success) {
        setSuccess("Seasonal pricing added successfully!");
        setShowPricingForm(false);
        loadSeasonalPricing();
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add pricing rule");
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePricing = async (pricingId: number) => {
    if (!confirm("Are you sure you want to delete this pricing rule?")) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await ApiService.deleteSeasonalPricing(pricingId);
      if (result.success) {
        setSuccess("Pricing rule deleted successfully!");
        loadSeasonalPricing();
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete pricing rule");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="room-management">
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

      <div className="tabs">
        <button
          className={`tab ${activeTab === "rooms" ? "active" : ""}`}
          onClick={() => setActiveTab("rooms")}
        >
          Rooms
        </button>
        <button
          className={`tab ${activeTab === "room-types" ? "active" : ""}`}
          onClick={() => setActiveTab("room-types")}
        >
          Room Types
        </button>
        <button
          className={`tab ${activeTab === "seasonal-pricing" ? "active" : ""}`}
          onClick={() => setActiveTab("seasonal-pricing")}
        >
          Seasonal Pricing
        </button>
      </div>

      {/* Rooms Tab */}
      {activeTab === "rooms" && (
        <div className="tab-content">
          <div className="content-header">
            <h2>Room Status Management</h2>
            <div className="header-stats">
              <span className="stat-badge stat-clean">
                Clean: {rooms.filter(r => r.status === "Clean" && !r.has_reservation).length}
              </span>
              <span className="stat-badge stat-reserved">
                Reserved: {rooms.filter(r => r.has_reservation).length}
              </span>
              <span className="stat-badge stat-occupied">
                Occupied: {rooms.filter(r => r.status === "Occupied").length}
              </span>
              <span className="stat-badge stat-dirty">
                Dirty: {rooms.filter(r => r.status === "Dirty").length}
              </span>
              <span className="stat-badge stat-maintenance">
                Maintenance: {rooms.filter(r => r.status === "Maintenance").length}
              </span>
            </div>
          </div>

          <div className="rooms-table-container">
            <table className="rooms-table">
              <thead>
                <tr>
                  <th>Room Number</th>
                  <th>Floor</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Base Price</th>
                  <th>Max Guests</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rooms.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: "center", padding: "2rem" }}>
                      {loading ? "Loading rooms..." : "No rooms found"}
                    </td>
                  </tr>
                ) : (
                  rooms
                    .sort((a, b) => {
                      if (a.floor !== b.floor) return a.floor - b.floor;
                      return a.room_number.localeCompare(b.room_number);
                    })
                    .map((room) => (
                      <tr key={room.room_id}>
                        <td className="room-number-cell">
                          <strong>{room.room_number}</strong>
                        </td>
                        <td>{room.floor}</td>
                        <td>{room.type_name}</td>
                        <td>
                          <span
                            className={`status-badge status-${room.status.toLowerCase()}`}
                          >
                            {room.has_reservation && room.status === "Clean"
                              ? `Reserved (${room.reservation_check_in})`
                              : room.status}
                          </span>
                        </td>
                        <td>¥{room.base_price}</td>
                        <td>{room.max_occupancy}</td>
                        <td className="actions-cell">
                          <div className="action-buttons">
                            {room.status === "Dirty" && (
                              <button
                                className="btn-action btn-clean"
                                onClick={() => handleUpdateRoomStatus(room.room_id, "Clean")}
                                disabled={loading}
                                title="Mark as Clean"
                              >
                                ✓ Clean
                              </button>
                            )}
                            {room.status === "Clean" && !room.has_reservation && (
                              <>
                                <button
                                  className="btn-action btn-dirty"
                                  onClick={() => handleUpdateRoomStatus(room.room_id, "Dirty")}
                                  disabled={loading}
                                  title="Mark as Dirty"
                                >
                                  ◐ Dirty
                                </button>
                                <button
                                  className="btn-action btn-maintenance"
                                  onClick={() => handleUpdateRoomStatus(room.room_id, "Maintenance")}
                                  disabled={loading}
                                  title="Mark for Maintenance"
                                >
                                  ⚠ Maintenance
                                </button>
                              </>
                            )}
                            {room.status === "Maintenance" && (
                              <button
                                className="btn-action btn-clean"
                                onClick={() => handleUpdateRoomStatus(room.room_id, "Clean")}
                                disabled={loading}
                                title="Mark as Clean"
                              >
                                ✓ Clean
                              </button>
                            )}
                            {room.status === "Occupied" && (
                              <span className="occupied-note">In use</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Room Types Tab */}
      {activeTab === "room-types" && (
        <div className="tab-content">
          <div className="content-header">
            <h2>Room Types</h2>
            <button onClick={handleAddRoomType} className="btn btn-primary">
              Add Room Type
            </button>
          </div>

          <div className="room-types-grid">
            {roomTypes.map((roomType) => (
              <div key={roomType.room_type_id} className="room-type-card">
                <div className="card-header">
                  <h3>{roomType.type_name}</h3>
                  <div className="card-price">¥{roomType.base_price}/night</div>
                </div>
                <div className="card-body">
                  <p className="description">{roomType.description}</p>
                  <div className="card-details">
                    <div className="detail-item">
                      <span className="label">Max Occupancy:</span>
                      <span className="value">
                        {roomType.max_occupancy} guests
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Amenities:</span>
                      <span className="value">{roomType.amenities}</span>
                    </div>
                  </div>
                </div>
                <div className="card-footer">
                  <button
                    onClick={() => handleEditRoomType(roomType)}
                    className="btn btn-info btn-sm"
                  >
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Seasonal Pricing Tab */}
      {activeTab === "seasonal-pricing" && (
        <div className="tab-content">
          <div className="content-header">
            <h2>Seasonal Pricing Rules</h2>
            <button onClick={handleAddPricing} className="btn btn-primary">
              Add Pricing Rule
            </button>
          </div>

          <div className="table-container">
            <table className="pricing-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Room Type</th>
                  <th>Season</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Multiplier</th>
                  <th>Fixed Price</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {seasonalPricing.map((pricing) => (
                  <tr key={pricing.pricing_id}>
                    <td>#{pricing.pricing_id}</td>
                    <td>{pricing.type_name}</td>
                    <td>{pricing.season_name}</td>
                    <td>{formatDate(pricing.start_date)}</td>
                    <td>{formatDate(pricing.end_date)}</td>
                    <td>
                      {pricing.price_multiplier
                        ? `${pricing.price_multiplier}x`
                        : "-"}
                    </td>
                    <td>
                      {pricing.fixed_price ? `¥${pricing.fixed_price}` : "-"}
                    </td>
                    <td>
                      <button
                        onClick={() => handleDeletePricing(pricing.pricing_id)}
                        className="btn btn-danger btn-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Room Type Form Modal */}
      {showRoomTypeForm && (
        <div
          className="modal-overlay"
          onClick={() => setShowRoomTypeForm(false)}
        >
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingRoomType ? "Edit Room Type" : "Add Room Type"}</h3>
              <button
                className="modal-close"
                onClick={() => setShowRoomTypeForm(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Type Name *</label>
                <input
                  type="text"
                  value={roomTypeForm.type_name}
                  onChange={(e) =>
                    setRoomTypeForm({
                      ...roomTypeForm,
                      type_name: e.target.value,
                    })
                  }
                  className="form-control"
                  placeholder="e.g., Deluxe Suite"
                />
              </div>
              <div className="form-group">
                <label>Description *</label>
                <textarea
                  value={roomTypeForm.description}
                  onChange={(e) =>
                    setRoomTypeForm({
                      ...roomTypeForm,
                      description: e.target.value,
                    })
                  }
                  className="form-control"
                  rows={3}
                  placeholder="Room description..."
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Base Price (¥) *</label>
                  <input
                    type="number"
                    value={roomTypeForm.base_price}
                    onChange={(e) =>
                      setRoomTypeForm({
                        ...roomTypeForm,
                        base_price: e.target.value,
                      })
                    }
                    className="form-control"
                    placeholder="400"
                    step="0.01"
                  />
                </div>
                <div className="form-group">
                  <label>Max Occupancy *</label>
                  <input
                    type="number"
                    value={roomTypeForm.max_occupancy}
                    onChange={(e) =>
                      setRoomTypeForm({
                        ...roomTypeForm,
                        max_occupancy: e.target.value,
                      })
                    }
                    className="form-control"
                    placeholder="2"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Amenities *</label>
                <input
                  type="text"
                  value={roomTypeForm.amenities}
                  onChange={(e) =>
                    setRoomTypeForm({
                      ...roomTypeForm,
                      amenities: e.target.value,
                    })
                  }
                  className="form-control"
                  placeholder="WiFi, TV, Air Conditioning"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                onClick={handleSaveRoomType}
                disabled={loading}
                className="btn btn-success"
              >
                {loading ? "Saving..." : "Save"}
              </button>
              <button
                onClick={() => setShowRoomTypeForm(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Seasonal Pricing Form Modal */}
      {showPricingForm && (
        <div
          className="modal-overlay"
          onClick={() => setShowPricingForm(false)}
        >
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Seasonal Pricing Rule</h3>
              <button
                className="modal-close"
                onClick={() => setShowPricingForm(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Room Type *</label>
                <select
                  value={pricingForm.room_type_id}
                  onChange={(e) =>
                    setPricingForm({
                      ...pricingForm,
                      room_type_id: e.target.value,
                    })
                  }
                  className="form-control"
                >
                  <option value="">Select room type</option>
                  {roomTypes.map((rt) => (
                    <option key={rt.room_type_id} value={rt.room_type_id}>
                      {rt.type_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Season Name *</label>
                <input
                  type="text"
                  value={pricingForm.season_name}
                  onChange={(e) =>
                    setPricingForm({
                      ...pricingForm,
                      season_name: e.target.value,
                    })
                  }
                  className="form-control"
                  placeholder="e.g., Spring Festival"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Start Date *</label>
                  <input
                    type="date"
                    value={pricingForm.start_date}
                    onChange={(e) =>
                      setPricingForm({
                        ...pricingForm,
                        start_date: e.target.value,
                      })
                    }
                    className="form-control"
                  />
                </div>
                <div className="form-group">
                  <label>End Date *</label>
                  <input
                    type="date"
                    value={pricingForm.end_date}
                    onChange={(e) =>
                      setPricingForm({
                        ...pricingForm,
                        end_date: e.target.value,
                      })
                    }
                    className="form-control"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Pricing Type *</label>
                <select
                  value={pricingForm.pricing_type}
                  onChange={(e) =>
                    setPricingForm({
                      ...pricingForm,
                      pricing_type: e.target.value,
                    })
                  }
                  className="form-control"
                >
                  <option value="multiplier">Price Multiplier</option>
                  <option value="fixed">Fixed Price</option>
                </select>
              </div>
              {pricingForm.pricing_type === "multiplier" ? (
                <div className="form-group">
                  <label>Price Multiplier *</label>
                  <input
                    type="number"
                    value={pricingForm.price_multiplier}
                    onChange={(e) =>
                      setPricingForm({
                        ...pricingForm,
                        price_multiplier: e.target.value,
                      })
                    }
                    className="form-control"
                    placeholder="1.5 (150% of base price)"
                    step="0.1"
                  />
                </div>
              ) : (
                <div className="form-group">
                  <label>Fixed Price (¥) *</label>
                  <input
                    type="number"
                    value={pricingForm.fixed_price}
                    onChange={(e) =>
                      setPricingForm({
                        ...pricingForm,
                        fixed_price: e.target.value,
                      })
                    }
                    className="form-control"
                    placeholder="800"
                    step="0.01"
                  />
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button
                onClick={handleSavePricing}
                disabled={loading}
                className="btn btn-success"
              >
                {loading ? "Saving..." : "Save"}
              </button>
              <button
                onClick={() => setShowPricingForm(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
