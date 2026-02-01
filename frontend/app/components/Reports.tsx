"use client";

import { useState } from "react";
import {
  ApiService,
  formatDateTime,
  OccupancyReport,
  RevenueReport,
  AuditLog,
  Backup,
} from "../lib/api";
import Toast from "./Toast";
import "../components/Reports.css";

type ReportType = "occupancy" | "revenue" | "audit" | "backup";

interface ReportsProps {
  defaultTab?: ReportType;
}

export default function Reports({ defaultTab = "occupancy" }: ReportsProps) {
  const [activeReport, setActiveReport] = useState<ReportType>(defaultTab);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Occupancy Report
  const [occupancyReport, setOccupancyReport] =
    useState<OccupancyReport | null>(null);
  const [occupancyDates, setOccupancyDates] = useState({
    start_date: "",
    end_date: "",
  });

  // Revenue Report
  const [revenueReport, setRevenueReport] = useState<RevenueReport | null>(
    null,
  );
  const [revenueDates, setRevenueDates] = useState({
    start_date: "",
    end_date: "",
  });

  // Audit Logs
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [auditFilters, setAuditFilters] = useState({
    operation_type: "",
    table_name: "",
    start_date: "",
    end_date: "",
  });

  // Backups
  const [backups, setBackups] = useState<Backup[]>([]);
  const [backupName, setBackupName] = useState("hrms_backup");

  const handleGenerateOccupancyReport = async () => {
    if (!occupancyDates.start_date || !occupancyDates.end_date) {
      setError("Please select start and end dates");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await ApiService.getOccupancyReport(
        occupancyDates.start_date,
        occupancyDates.end_date,
      );
      setOccupancyReport(data);
      setSuccess("Occupancy report generated successfully!");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate report");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRevenueReport = async () => {
    if (!revenueDates.start_date || !revenueDates.end_date) {
      setError("Please select start and end dates");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await ApiService.getRevenueReport(
        revenueDates.start_date,
        revenueDates.end_date,
      );
      setRevenueReport(data);
      setSuccess("Revenue report generated successfully!");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate report");
    } finally {
      setLoading(false);
    }
  };

  const handleSearchAuditLogs = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await ApiService.getAuditLogs({
        operation_type: auditFilters.operation_type || undefined,
        table_name: auditFilters.table_name || undefined,
        start_date: auditFilters.start_date || undefined,
        end_date: auditFilters.end_date || undefined,
        limit: 50,
      });
      setAuditLogs(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load audit logs");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadBackups = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await ApiService.getBackupHistory();
      setBackups(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load backup history");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    if (!backupName) {
      setError("Please enter a backup name");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await ApiService.createBackup(backupName);
      if (result.success) {
        setSuccess("Backup created successfully!");
        handleLoadBackups();
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create backup");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reports-container">
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

      <div className="reports-tabs">
        <button
          className={`report-tab ${activeReport === "occupancy" ? "active" : ""}`}
          onClick={() => setActiveReport("occupancy")}
        >
          Occupancy Report
        </button>
        <button
          className={`report-tab ${activeReport === "revenue" ? "active" : ""}`}
          onClick={() => setActiveReport("revenue")}
        >
          Revenue Report
        </button>
        <button
          className={`report-tab ${activeReport === "audit" ? "active" : ""}`}
          onClick={() => setActiveReport("audit")}
        >
          Audit Logs
        </button>
        <button
          className={`report-tab ${activeReport === "backup" ? "active" : ""}`}
          onClick={() => {
            setActiveReport("backup");
            handleLoadBackups();
          }}
        >
          Backup Management
        </button>
      </div>

      {/* Occupancy Report */}
      {activeReport === "occupancy" && (
        <div className="report-content">
          <h2>Occupancy Rate Report</h2>
          <div className="report-form">
            <div className="form-row">
              <div className="form-group">
                <label>Start Date</label>
                <input
                  type="date"
                  value={occupancyDates.start_date}
                  onChange={(e) =>
                    setOccupancyDates({
                      ...occupancyDates,
                      start_date: e.target.value,
                    })
                  }
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>End Date</label>
                <input
                  type="date"
                  value={occupancyDates.end_date}
                  onChange={(e) =>
                    setOccupancyDates({
                      ...occupancyDates,
                      end_date: e.target.value,
                    })
                  }
                  className="form-control"
                />
              </div>
            </div>
            <button
              onClick={handleGenerateOccupancyReport}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? "Generating..." : "Generate Report"}
            </button>
          </div>

          {occupancyReport && (
            <div className="report-results">
              <div className="stats-summary">
                <div className="stat-card">
                  <div className="stat-label">Report Period</div>
                  <div className="stat-value">
                    {occupancyReport.start_date} to {occupancyReport.end_date}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Total Days</div>
                  <div className="stat-value">{occupancyReport.days}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Average Occupancy</div>
                  <div className="stat-value highlight">
                    {occupancyReport.average_occupancy_rate.toFixed(2)}%
                  </div>
                </div>
              </div>

              <h3>Daily Occupancy Data</h3>
              <div className="table-container">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Total Rooms</th>
                      <th>Occupied</th>
                      <th>Available</th>
                      <th>Occupancy Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {occupancyReport.daily_data.map((day, index) => (
                      <tr key={index}>
                        <td>{day.date}</td>
                        <td>{day.total_rooms}</td>
                        <td>{day.occupied_rooms}</td>
                        <td>{day.available_rooms}</td>
                        <td>
                          <span className="rate-badge">
                            {day.occupancy_rate.toFixed(2)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Revenue Report */}
      {activeReport === "revenue" && (
        <div className="report-content">
          <h2>Revenue Report</h2>
          <div className="report-form">
            <div className="form-row">
              <div className="form-group">
                <label>Start Date</label>
                <input
                  type="date"
                  value={revenueDates.start_date}
                  onChange={(e) =>
                    setRevenueDates({
                      ...revenueDates,
                      start_date: e.target.value,
                    })
                  }
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>End Date</label>
                <input
                  type="date"
                  value={revenueDates.end_date}
                  onChange={(e) =>
                    setRevenueDates({
                      ...revenueDates,
                      end_date: e.target.value,
                    })
                  }
                  className="form-control"
                />
              </div>
            </div>
            <button
              onClick={handleGenerateRevenueReport}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? "Generating..." : "Generate Report"}
            </button>
          </div>

          {revenueReport && (
            <div className="report-results">
              <div className="stats-summary">
                <div className="stat-card">
                  <div className="stat-label">Total Reservations</div>
                  <div className="stat-value">
                    {revenueReport.total_reservations}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Total Revenue</div>
                  <div className="stat-value highlight">
                    ¥{revenueReport.total_revenue.toFixed(2)}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Avg per Reservation</div>
                  <div className="stat-value">
                    ¥{revenueReport.average_revenue_per_reservation.toFixed(2)}
                  </div>
                </div>
              </div>

              <h3>Revenue by Room Type</h3>
              <div className="table-container">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>Room Type</th>
                      <th>Reservations</th>
                      <th>Revenue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {revenueReport.by_room_type.map((item, index) => (
                      <tr key={index}>
                        <td>{item.room_type}</td>
                        <td>{item.reservations}</td>
                        <td className="revenue">¥{item.revenue.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <h3>Revenue by Payment Method</h3>
              <div className="table-container">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>Payment Method</th>
                      <th>Transactions</th>
                      <th>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {revenueReport.by_payment_method.map((item, index) => (
                      <tr key={index}>
                        <td>{item.payment_method}</td>
                        <td>{item.count}</td>
                        <td className="revenue">¥{item.amount.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Audit Logs */}
      {activeReport === "audit" && (
        <div className="report-content">
          <h2>Audit Logs</h2>
          <div className="report-form">
            <div className="form-row">
              <div className="form-group">
                <label>Operation Type</label>
                <input
                  type="text"
                  value={auditFilters.operation_type}
                  onChange={(e) =>
                    setAuditFilters({
                      ...auditFilters,
                      operation_type: e.target.value,
                    })
                  }
                  placeholder="CREATE, UPDATE, DELETE, etc."
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>Table Name</label>
                <input
                  type="text"
                  value={auditFilters.table_name}
                  onChange={(e) =>
                    setAuditFilters({
                      ...auditFilters,
                      table_name: e.target.value,
                    })
                  }
                  placeholder="reservations, rooms, etc."
                  className="form-control"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Start Date</label>
                <input
                  type="date"
                  value={auditFilters.start_date}
                  onChange={(e) =>
                    setAuditFilters({
                      ...auditFilters,
                      start_date: e.target.value,
                    })
                  }
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>End Date</label>
                <input
                  type="date"
                  value={auditFilters.end_date}
                  onChange={(e) =>
                    setAuditFilters({
                      ...auditFilters,
                      end_date: e.target.value,
                    })
                  }
                  className="form-control"
                />
              </div>
            </div>
            <button
              onClick={handleSearchAuditLogs}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? "Searching..." : "Search Logs"}
            </button>
          </div>

          {auditLogs.length > 0 && (
            <div className="report-results">
              <h3>Audit Log Entries ({auditLogs.length})</h3>
              <div className="table-container">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>User</th>
                      <th>Operation</th>
                      <th>Table</th>
                      <th>Record ID</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log) => (
                      <tr key={log.audit_id}>
                        <td>{formatDateTime(log.timestamp)}</td>
                        <td>{log.username}</td>
                        <td>
                          <span
                            className={`operation-badge ${log.operation_type.toLowerCase()}`}
                          >
                            {log.operation_type}
                          </span>
                        </td>
                        <td>{log.table_name || "-"}</td>
                        <td>{log.record_id || "-"}</td>
                        <td className="description">
                          {log.description || "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Backup Management */}
      {activeReport === "backup" && (
        <div className="report-content">
          <h2>Database Backup Management</h2>
          <div className="backup-create">
            <h3>Create New Backup</h3>
            <div className="form-group">
              <label>Backup Name</label>
              <input
                type="text"
                value={backupName}
                onChange={(e) => setBackupName(e.target.value)}
                placeholder="hrms_backup"
                className="form-control"
              />
            </div>
            <button
              onClick={handleCreateBackup}
              disabled={loading}
              className="btn btn-success"
            >
              {loading ? "Creating..." : "Create Backup"}
            </button>
          </div>

          {backups.length > 0 && (
            <div className="report-results">
              <h3>Backup History ({backups.length})</h3>
              <div className="table-container">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Filename</th>
                      <th>Size (KB)</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th>Created By</th>
                      <th>Created At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {backups.map((backup) => (
                      <tr key={backup.backup_id}>
                        <td>#{backup.backup_id}</td>
                        <td>
                          {backup.backup_file.split("/").pop() ||
                            backup.backup_file}
                        </td>
                        <td>{(backup.backup_size / 1024).toFixed(2)}</td>
                        <td>{backup.backup_type}</td>
                        <td>
                          <span
                            className={`status-badge ${backup.status.toLowerCase()}`}
                          >
                            {backup.status}
                          </span>
                        </td>
                        <td>{backup.username}</td>
                        <td>{formatDateTime(backup.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
