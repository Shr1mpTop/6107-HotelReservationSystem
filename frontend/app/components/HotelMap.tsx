"use client";

import { useState, useEffect } from "react";
import { Room } from "../lib/api";
import "./HotelMap.css";

interface HotelMapProps {
  rooms: Room[];
  onRoomClick?: (room: Room) => void;
}

export default function HotelMap({ rooms, onRoomClick }: HotelMapProps) {
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [hoveredRoom, setHoveredRoom] = useState<string | null>(null);

  // Group rooms by floor
  const roomsByFloor = rooms.reduce(
    (acc, room) => {
      const floor = room.floor || 1;
      if (!acc[floor]) acc[floor] = [];
      acc[floor].push(room);
      return acc;
    },
    {} as Record<number, Room[]>,
  );

  const handleRoomClick = (room: Room) => {
    setSelectedRoom(room);
    if (onRoomClick) {
      onRoomClick(room);
    }
  };

  const getStatusColor = (status: string, hasReservation?: boolean) => {
    // If room is clean but has a reservation, show yellow/orange
    if (status.toLowerCase() === "clean" && hasReservation) {
      return "#f59e0b"; // Orange for reserved
    }

    switch (status.toLowerCase()) {
      case "clean":
        return "#10b981"; // Green
      case "occupied":
        return "#ef4444"; // Red
      case "dirty":
        return "#f59e0b"; // Orange
      case "maintenance":
        return "#6366f1"; // Blue
      default:
        return "#9ca3af"; // Gray
    }
  };

  const getStatusIcon = (status: string, hasReservation?: boolean) => {
    // If room is clean but has a reservation, show reservation icon
    if (status.toLowerCase() === "clean" && hasReservation) {
      return "📅"; // Calendar icon for reserved
    }

    switch (status.toLowerCase()) {
      case "clean":
        return "✓";
      case "occupied":
        return "◆";
      case "dirty":
        return "◐";
      case "maintenance":
        return "⚠";
      default:
        return "?";
    }
  };

  const getRoomTypeClass = (typeName: string) => {
    if (typeName.toLowerCase().includes("single")) return "room-single";
    if (typeName.toLowerCase().includes("double")) return "room-double";
    if (typeName.toLowerCase().includes("suite")) return "room-suite";
    return "room-standard";
  };

  return (
    <div className="hotel-map-container">
      <div className="hotel-map-header">
        <h2>🏨 Hotel Floor Map</h2>
        <div className="map-legend">
          <div className="legend-item">
            <span
              className="legend-dot"
              style={{ background: "#10b981" }}
            ></span>
            <span>Available</span>
          </div>
          <div className="legend-item">
            <span
              className="legend-dot"
              style={{ background: "#f59e0b" }}
            ></span>
            <span>Reserved</span>
          </div>
          <div className="legend-item">
            <span
              className="legend-dot"
              style={{ background: "#ef4444" }}
            ></span>
            <span>Occupied</span>
          </div>
          <div className="legend-item">
            <span
              className="legend-dot"
              style={{ background: "#f59e0b" }}
            ></span>
            <span>Dirty</span>
          </div>
          <div className="legend-item">
            <span
              className="legend-dot"
              style={{ background: "#6366f1" }}
            ></span>
            <span>Maintenance</span>
          </div>
        </div>
      </div>

      <div className="floors-container">
        {[3, 2, 1].map((floorNum) => {
          const floorRooms = roomsByFloor[floorNum] || [];
          if (floorRooms.length === 0) return null;

          return (
            <div key={floorNum} className="floor-section">
              <div className="floor-header">
                <div className="floor-number">Floor {floorNum}</div>
                <div className="floor-stats">
                  {
                    floorRooms.filter(
                      (r) => r.status === "Clean" && !r.has_reservation,
                    ).length
                  }{" "}
                  Available
                  <span className="divider">|</span>
                  {
                    floorRooms.filter(
                      (r) => r.has_reservation && r.status === "Clean",
                    ).length
                  }{" "}
                  Reserved
                  <span className="divider">|</span>
                  {
                    floorRooms.filter((r) => r.status === "Occupied").length
                  }{" "}
                  Occupied
                </div>
              </div>

              <div className="rooms-floor-grid">
                {floorRooms
                  .sort((a, b) => a.room_number.localeCompare(b.room_number))
                  .map((room) => (
                    <div
                      key={room.room_id}
                      className={`room-item ${getRoomTypeClass(room.type_name)} ${
                        selectedRoom?.room_id === room.room_id ? "selected" : ""
                      } ${hoveredRoom === room.room_number ? "hovered" : ""}`}
                      onClick={() => handleRoomClick(room)}
                      onMouseEnter={() => setHoveredRoom(room.room_number)}
                      onMouseLeave={() => setHoveredRoom(null)}
                      style={{
                        borderColor: getStatusColor(
                          room.status,
                          room.has_reservation,
                        ),
                        boxShadow:
                          selectedRoom?.room_id === room.room_id
                            ? `0 0 20px ${getStatusColor(room.status, room.has_reservation)}`
                            : undefined,
                      }}
                    >
                      <div className="room-item-header">
                        <span className="room-item-number">
                          {room.room_number}
                        </span>
                        <span
                          className="room-item-status-icon"
                          style={{
                            color: getStatusColor(
                              room.status,
                              room.has_reservation,
                            ),
                          }}
                        >
                          {getStatusIcon(room.status, room.has_reservation)}
                        </span>
                      </div>
                      <div className="room-item-type">{room.type_name}</div>
                      <div
                        className="room-item-status"
                        style={{
                          color: getStatusColor(
                            room.status,
                            room.has_reservation,
                          ),
                        }}
                      >
                        {room.has_reservation && room.status === "Clean"
                          ? `Reserved (${room.reservation_check_in})`
                          : room.status}
                      </div>
                      <div className="room-item-price">¥{room.base_price}</div>
                    </div>
                  ))}
              </div>
            </div>
          );
        })}
      </div>

      {selectedRoom && (
        <div className="room-detail-panel">
          <div className="detail-panel-header">
            <h3>Room {selectedRoom.room_number} Details</h3>
            <button className="close-btn" onClick={() => setSelectedRoom(null)}>
              ×
            </button>
          </div>
          <div className="detail-panel-content">
            <div className="detail-row">
              <span className="detail-label">Type:</span>
              <span className="detail-value">{selectedRoom.type_name}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Status:</span>
              <span
                className="detail-value"
                style={{
                  color: getStatusColor(
                    selectedRoom.status,
                    selectedRoom.has_reservation,
                  ),
                }}
              >
                {getStatusIcon(
                  selectedRoom.status,
                  selectedRoom.has_reservation,
                )}{" "}
                {selectedRoom.has_reservation && selectedRoom.status === "Clean"
                  ? `Reserved (Check-in: ${selectedRoom.reservation_check_in})`
                  : selectedRoom.status}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Floor:</span>
              <span className="detail-value">{selectedRoom.floor}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Base Price:</span>
              <span className="detail-value">
                ¥{selectedRoom.base_price}/night
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Max Occupancy:</span>
              <span className="detail-value">
                {selectedRoom.max_occupancy} guests
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
