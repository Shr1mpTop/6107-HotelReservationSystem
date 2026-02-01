"use client";

import { DashboardStats } from "../lib/api";
import "./StatsCharts.css";

interface StatsChartsProps {
  stats: DashboardStats;
}

export default function StatsCharts({ stats }: StatsChartsProps) {
  const occupancyPercentage = stats.occupancy_rate;
  const availablePercentage = (stats.available_rooms / stats.total_rooms) * 100;
  const occupiedPercentage = (stats.occupied_rooms / stats.total_rooms) * 100;
  const maintenancePercentage = 100 - occupancyPercentage - availablePercentage;

  return (
    <div className="stats-charts-container">
      {/* Main Stats Cards with Animation */}
      <div className="stats-cards-grid">
        <div className="stat-card-modern card-total">
          <div className="card-icon-wrapper">
            <div className="card-icon">🏨</div>
          </div>
          <div className="card-content">
            <div className="card-value">{stats.total_rooms}</div>
            <div className="card-label">Total Rooms</div>
          </div>
          <div className="card-bg-decoration"></div>
        </div>

        <div className="stat-card-modern card-available">
          <div className="card-icon-wrapper">
            <div className="card-icon">✓</div>
          </div>
          <div className="card-content">
            <div className="card-value">{stats.available_rooms}</div>
            <div className="card-label">Available</div>
            <div className="card-percentage">
              {availablePercentage.toFixed(1)}%
            </div>
          </div>
          <div className="card-bg-decoration"></div>
        </div>

        <div className="stat-card-modern card-occupied">
          <div className="card-icon-wrapper">
            <div className="card-icon">◆</div>
          </div>
          <div className="card-content">
            <div className="card-value">{stats.occupied_rooms}</div>
            <div className="card-label">Occupied</div>
            <div className="card-percentage">
              {occupiedPercentage.toFixed(1)}%
            </div>
          </div>
          <div className="card-bg-decoration"></div>
        </div>

        <div className="stat-card-modern card-occupancy">
          <div className="card-icon-wrapper">
            <div className="card-icon">📊</div>
          </div>
          <div className="card-content">
            <div className="card-value">{stats.occupancy_rate}%</div>
            <div className="card-label">Occupancy Rate</div>
          </div>
          <div className="card-bg-decoration"></div>
        </div>
      </div>

      {/* Circular Progress Chart */}
      <div className="chart-section">
        <h3 className="chart-title">Occupancy Overview</h3>
        <div className="circular-chart-container">
          <svg className="circular-chart" viewBox="0 0 200 200">
            {/* Background Circle */}
            <circle
              cx="100"
              cy="100"
              r="80"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
            />

            {/* Occupancy Arc */}
            <circle
              cx="100"
              cy="100"
              r="80"
              fill="none"
              stroke="#ef4444"
              strokeWidth="20"
              strokeDasharray={`${(occupancyPercentage / 100) * 502.4} 502.4`}
              strokeDashoffset="0"
              transform="rotate(-90 100 100)"
              className="progress-circle occupied-arc"
            />

            {/* Center Text */}
            <text
              x="100"
              y="95"
              textAnchor="middle"
              className="chart-percentage"
            >
              {stats.occupancy_rate}%
            </text>
            <text x="100" y="115" textAnchor="middle" className="chart-label">
              Occupied
            </text>
          </svg>

          {/* Legend */}
          <div className="chart-legend">
            <div className="legend-row">
              <span className="legend-color occupied"></span>
              <span className="legend-text">
                Occupied: {stats.occupied_rooms}
              </span>
            </div>
            <div className="legend-row">
              <span className="legend-color available"></span>
              <span className="legend-text">
                Available: {stats.available_rooms}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Bar Chart Visualization */}
      <div className="chart-section">
        <h3 className="chart-title">Room Status Distribution</h3>
        <div className="bar-chart">
          <div className="bar-item">
            <div className="bar-label">Available</div>
            <div className="bar-track">
              <div
                className="bar-fill bar-available"
                style={{ width: `${availablePercentage}%` }}
              >
                <span className="bar-value">{stats.available_rooms}</span>
              </div>
            </div>
          </div>

          <div className="bar-item">
            <div className="bar-label">Occupied</div>
            <div className="bar-track">
              <div
                className="bar-fill bar-occupied"
                style={{ width: `${occupiedPercentage}%` }}
              >
                <span className="bar-value">{stats.occupied_rooms}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Status Indicator */}
      <div className="status-indicator">
        <div className="status-dot pulsing"></div>
        <span>Live Status - Auto-refresh enabled</span>
      </div>
    </div>
  );
}
