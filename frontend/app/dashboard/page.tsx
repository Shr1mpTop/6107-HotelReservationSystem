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
import HotelMap from "../components/HotelMap";
import StatsCharts from "../components/StatsCharts";
import Loading from "../components/Loading";
import ReservationForm from "../components/ReservationForm";
import CheckInForm from "../components/CheckInForm";
import CheckOutForm from "../components/CheckOutForm";
import ReservationSearch from "../components/ReservationSearch";
import GuestsList from "../components/GuestsList";
import RoomManagement from "../components/RoomManagement";
import Reports from "../components/Reports";
import Settings from "../components/Settings";

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
    loadRooms(); // Load rooms for hotel map

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      if (activeSection === "dashboard" || activeSection === "hotel-map") {
        loadDashboardStats();
        loadRooms();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [router, activeSection]);

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
      const data = await ApiService.getRoomsWithReservations();
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
      {loading && (
        <Loading
          text="Loading Hotel Data..."
          subtext="Please wait while we fetch the latest information"
        />
      )}

      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="nav-brand">
          <h2>🏨 HRMS Dashboard</h2>
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
            className={`menu-item ${activeSection === "hotel-map" ? "active" : ""}`}
            onClick={() => handleSectionChange("hotel-map")}
          >
            <span className="menu-icon">M</span>
            <span>Hotel Map</span>
          </div>

          {/* Reservation Management */}
          <div className="menu-category">Reservations</div>
          <div
            className={`menu-item ${activeSection === "new-reservation" ? "active" : ""}`}
            onClick={() => handleSectionChange("new-reservation")}
          >
            <span className="menu-icon">+</span>
            <span>New Reservation</span>
          </div>
          <div
            className={`menu-item ${activeSection === "reservations" ? "active" : ""}`}
            onClick={() => handleSectionChange("reservations")}
          >
            <span className="menu-icon">◷</span>
            <span>All Reservations</span>
          </div>
          <div
            className={`menu-item ${activeSection === "today-checkins" ? "active" : ""}`}
            onClick={() => handleSectionChange("today-checkins")}
          >
            <span className="menu-icon">T</span>
            <span>Today Check-ins</span>
          </div>
          <div
            className={`menu-item ${activeSection === "current-guests" ? "active" : ""}`}
            onClick={() => handleSectionChange("current-guests")}
          >
            <span className="menu-icon">G</span>
            <span>Current Guests</span>
          </div>

          {/* Operations */}
          <div className="menu-category">Operations</div>
          <div
            className={`menu-item ${activeSection === "check-in" ? "active" : ""}`}
            onClick={() => handleSectionChange("check-in")}
          >
            <span className="menu-icon">I</span>
            <span>Check-in</span>
          </div>
          <div
            className={`menu-item ${activeSection === "check-out" ? "active" : ""}`}
            onClick={() => handleSectionChange("check-out")}
          >
            <span className="menu-icon">O</span>
            <span>Check-out</span>
          </div>

          {/* Room Management */}
          <div className="menu-category">Rooms</div>
          <div
            className={`menu-item ${activeSection === "rooms" ? "active" : ""}`}
            onClick={() => handleSectionChange("rooms")}
          >
            <span className="menu-icon">▢</span>
            <span>Room List</span>
          </div>
          {user?.role === "admin" && (
            <>
              <div
                className={`menu-item ${activeSection === "room-types" ? "active" : ""}`}
                onClick={() => handleSectionChange("room-types")}
              >
                <span className="menu-icon">R</span>
                <span>Room Types</span>
              </div>
              <div
                className={`menu-item ${activeSection === "pricing" ? "active" : ""}`}
                onClick={() => handleSectionChange("pricing")}
              >
                <span className="menu-icon">¥</span>
                <span>Seasonal Pricing</span>
              </div>
            </>
          )}

          {/* Reports (Admin only) */}
          {user?.role === "admin" && (
            <>
              <div className="menu-category">Reports</div>
              <div
                className={`menu-item ${activeSection === "occupancy-report" ? "active" : ""}`}
                onClick={() => handleSectionChange("occupancy-report")}
              >
                <span className="menu-icon">%</span>
                <span>Occupancy Report</span>
              </div>
              <div
                className={`menu-item ${activeSection === "revenue-report" ? "active" : ""}`}
                onClick={() => handleSectionChange("revenue-report")}
              >
                <span className="menu-icon">$</span>
                <span>Revenue Report</span>
              </div>
              <div
                className={`menu-item ${activeSection === "audit-logs" ? "active" : ""}`}
                onClick={() => handleSectionChange("audit-logs")}
              >
                <span className="menu-icon">A</span>
                <span>Audit Logs</span>
              </div>
            </>
          )}

          {/* System */}
          <div className="menu-category">System</div>
          <div
            className={`menu-item ${activeSection === "settings" ? "active" : ""}`}
            onClick={() => handleSectionChange("settings")}
          >
            <span className="menu-icon">S</span>
            <span>Settings</span>
          </div>
        </div>

        {/* Content Area */}
        <div className="content">
          {error && <div className="alert alert-error">{error}</div>}

          {/* Dashboard Section */}
          {activeSection === "dashboard" && (
            <div>
              <h2 className="section-header">Dashboard Overview</h2>
              {stats ? (
                <StatsCharts stats={stats} />
              ) : (
                <p>Loading statistics...</p>
              )}
            </div>
          )}

          {/* Hotel Map Section */}
          {activeSection === "hotel-map" && (
            <div>
              <h2 className="section-header">Interactive Hotel Map</h2>
              {rooms.length > 0 ? (
                <HotelMap rooms={rooms} onRoomUpdate={loadRooms} />
              ) : (
                <div style={{ textAlign: "center", padding: "3rem" }}>
                  <p>Loading hotel map...</p>
                </div>
              )}
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
              <h2 className="section-header">Search & Manage Reservations</h2>
              <ReservationSearch />
            </div>
          )}

          {/* New Reservation Section */}
          {activeSection === "new-reservation" && (
            <div>
              <h2 className="section-header">Create New Reservation</h2>
              <ReservationForm
                onSuccess={() => {
                  // Refresh data and switch to reservations view
                  loadReservations();
                  loadDashboardStats();
                  loadRooms(); // Refresh rooms to show reservation status
                  setTimeout(() => setActiveSection("reservations"), 2000);
                }}
              />
            </div>
          )}

          {/* Check-in Section */}
          {activeSection === "check-in" && (
            <div>
              <h2 className="section-header">Guest Check-in</h2>
              <CheckInForm />
            </div>
          )}

          {/* Check-out Section */}
          {activeSection === "check-out" && (
            <div>
              <h2 className="section-header">Guest Check-out</h2>
              <CheckOutForm />
            </div>
          )}

          {/* Today Check-ins Section */}
          {activeSection === "today-checkins" && (
            <div>
              <h2 className="section-header">Today's Expected Check-ins</h2>
              <GuestsList type="today-checkins" />
            </div>
          )}

          {/* Current Guests Section */}
          {activeSection === "current-guests" && (
            <div>
              <h2 className="section-header">Current Guests</h2>
              <GuestsList type="current-guests" />
            </div>
          )}

          {/* Room Types and Pricing Section */}
          {activeSection === "room-types" && user?.role === "admin" && (
            <div>
              <h2 className="section-header">Room Type & Pricing Management</h2>
              <RoomManagement defaultTab="room-types" />
            </div>
          )}

          {/* Seasonal Pricing Section */}
          {activeSection === "pricing" && user?.role === "admin" && (
            <div>
              <h2 className="section-header">Seasonal Pricing Management</h2>
              <RoomManagement defaultTab="seasonal-pricing" />
            </div>
          )}

          {/* Occupancy Report Section */}
          {activeSection === "occupancy-report" && user?.role === "admin" && (
            <div>
              <h2 className="section-header">Reports & System Management</h2>
              <Reports />
            </div>
          )}

          {/* Revenue Report Section (same Reports component, different tab) */}
          {activeSection === "revenue-report" && user?.role === "admin" && (
            <div>
              <h2 className="section-header">Reports & System Management</h2>
              <Reports defaultTab="revenue" />
            </div>
          )}

          {/* Audit Logs Section (same Reports component, different tab) */}
          {activeSection === "audit-logs" && user?.role === "admin" && (
            <div>
              <h2 className="section-header">Reports & System Management</h2>
              <Reports defaultTab="audit" />
            </div>
          )}

          {/* Settings Section */}
          {activeSection === "settings" && (
            <div>
              <h2 className="section-header">System Settings</h2>
              <Settings />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
