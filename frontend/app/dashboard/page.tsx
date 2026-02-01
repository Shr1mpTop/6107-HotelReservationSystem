"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  AuthService,
  ApiService,
  User,
  DashboardStats,
  Room,
  Reservation,
} from "../lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [activeSection, setActiveSection] = useState("dashboard");
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Check authentication
    if (!AuthService.isAuthenticated()) {
      router.push("/login");
      return;
    }

    const currentUser = AuthService.getUser();
    if (currentUser) {
      setUser(currentUser);
    }

    // Load initial data
    loadDashboardStats();
  }, [router]);

  const loadDashboardStats = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        AuthService.removeToken();
        router.push("/login");
      } else {
        setError("Failed to load dashboard data");
      }
    } finally {
      setLoading(false);
    }
  };

  const loadRooms = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getRooms();
      setRooms(data);
    } catch (err) {
      setError("Failed to load rooms");
    } finally {
      setLoading(false);
    }
  };

  const loadReservations = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getReservations();
      setReservations(data);
    } catch (err) {
      setError("Failed to load reservations");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await AuthService.logout();
    router.push("/login");
  };

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
    setError("");

    if (section === "dashboard") {
      loadDashboardStats();
    } else if (section === "rooms") {
      loadRooms();
    } else if (section === "reservations") {
      loadReservations();
    }
  };

  return (
    <>
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="nav-brand">
          <h2>HRMS Dashboard</h2>
        </div>
        <div className="nav-menu">
          <span className="user-info">
            {user?.full_name} ({user?.role})
          </span>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </nav>

      {/* Main Container */}
      <div className="main-container">
        {/* Sidebar */}
        <div className="sidebar">
          <div
            className={`menu-item ${activeSection === "dashboard" ? "active" : ""}`}
            onClick={() => handleSectionChange("dashboard")}
          >
            <span className="menu-icon">▣</span>
            <span>Dashboard</span>
          </div>
          <div
            className={`menu-item ${activeSection === "rooms" ? "active" : ""}`}
            onClick={() => handleSectionChange("rooms")}
          >
            <span className="menu-icon">▢</span>
            <span>Rooms</span>
          </div>
          <div
            className={`menu-item ${activeSection === "reservations" ? "active" : ""}`}
            onClick={() => handleSectionChange("reservations")}
          >
            <span className="menu-icon">◷</span>
            <span>Reservations</span>
          </div>
          <div
            className={`menu-item ${activeSection === "new-reservation" ? "active" : ""}`}
            onClick={() => handleSectionChange("new-reservation")}
          >
            <span className="menu-icon">+</span>
            <span>New Reservation</span>
          </div>
        </div>

        {/* Content Area */}
        <div className="content">
          {error && <div className="alert alert-error">{error}</div>}

          {/* Dashboard Section */}
          {activeSection === "dashboard" && (
            <div>
              <h2 className="section-header">Dashboard Overview</h2>
              {stats && (
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-icon">R</div>
                    <div className="stat-info">
                      <h3>{stats.total_rooms}</h3>
                      <p>Total Rooms</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">A</div>
                    <div className="stat-info">
                      <h3>{stats.available_rooms}</h3>
                      <p>Available Rooms</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">O</div>
                    <div className="stat-info">
                      <h3>{stats.occupied_rooms}</h3>
                      <p>Occupied Rooms</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">%</div>
                    <div className="stat-info">
                      <h3>{stats.occupancy_rate}%</h3>
                      <p>Occupancy Rate</p>
                    </div>
                  </div>
                </div>
              )}
              <div
                style={{
                  background: "white",
                  padding: "2rem",
                  borderRadius: "10px",
                  boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                }}
              >
                <h3>System Status</h3>
                <p>All services are operational.</p>
              </div>
            </div>
          )}

          {/* Rooms Section */}
          {activeSection === "rooms" && (
            <div>
              <h2 className="section-header">Room Management</h2>
              <button
                onClick={loadRooms}
                className="btn btn-primary"
                style={{ marginBottom: "1.5rem" }}
              >
                Refresh Rooms
              </button>
              <div className="rooms-grid">
                {rooms.map((room) => (
                  <div key={room.room_id} className="room-card">
                    <div className="room-header">
                      <div className="room-number">Room {room.room_number}</div>
                      <span
                        className={`room-status ${room.status.toLowerCase().replace(" ", "-")}`}
                      >
                        {room.status}
                      </span>
                    </div>
                    <div className="room-info">
                      <p>
                        <strong>Type:</strong> {room.type_name}
                      </p>
                      <p>
                        <strong>Floor:</strong> {room.floor}
                      </p>
                      <p>
                        <strong>Max Occupancy:</strong> {room.max_occupancy}
                      </p>
                      <p>
                        <strong>Base Price:</strong> ¥{room.base_price}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reservations Section */}
          {activeSection === "reservations" && (
            <div>
              <h2 className="section-header">Reservation Management</h2>
              <button
                onClick={loadReservations}
                className="btn btn-primary"
                style={{ marginBottom: "1.5rem" }}
              >
                Refresh
              </button>
              {reservations.length > 0 ? (
                <div className="table-container">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Guest</th>
                        <th>Room</th>
                        <th>Check-in</th>
                        <th>Check-out</th>
                        <th>Status</th>
                        <th>Total Price</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reservations.map((reservation) => (
                        <tr key={reservation.reservation_id}>
                          <td>#{reservation.reservation_id}</td>
                          <td>
                            {reservation.guest_first_name}{" "}
                            {reservation.guest_last_name}
                          </td>
                          <td>Room {reservation.room_number}</td>
                          <td>
                            {new Date(
                              reservation.check_in_date,
                            ).toLocaleDateString()}
                          </td>
                          <td>
                            {new Date(
                              reservation.check_out_date,
                            ).toLocaleDateString()}
                          </td>
                          <td>
                            <span
                              className={`status ${reservation.status.toLowerCase()}`}
                            >
                              {reservation.status}
                            </span>
                          </td>
                          <td>¥{reservation.total_price}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No reservations found.</p>
              )}
            </div>
          )}

          {/* New Reservation Section */}
          {activeSection === "new-reservation" && (
            <div>
              <h2 className="section-header">Create New Reservation</h2>
              <div
                style={{
                  background: "white",
                  padding: "2rem",
                  borderRadius: "10px",
                  boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                }}
              >
                <p>New reservation form will be available here.</p>
                <p>This feature is under development.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
