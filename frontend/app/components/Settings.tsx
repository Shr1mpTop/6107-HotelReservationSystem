"use client";

import { useState } from "react";
import { ApiService, AuthService, User } from "../lib/api";
import Toast from "./Toast";
import "../components/Settings.css";

export default function Settings() {
  const [user, setUser] = useState<User | null>(AuthService.getUser());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [passwordForm, setPasswordForm] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });

  const handleChangePassword = async () => {
    if (!passwordForm.old_password || !passwordForm.new_password) {
      setError("Please fill in all password fields");
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError("New passwords do not match");
      return;
    }

    if (passwordForm.new_password.length < 6) {
      setError("New password must be at least 6 characters long");
      return;
    }

    if (!user) {
      setError("User not found");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await ApiService.changePassword(
        user.user_id,
        passwordForm.old_password,
        passwordForm.new_password,
      );

      if (result.success) {
        setSuccess("Password changed successfully!");
        setPasswordForm({
          old_password: "",
          new_password: "",
          confirm_password: "",
        });
      } else {
        setError(result.message || "Failed to change password");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to change password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-container">
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

      <h2 className="settings-title">System Settings</h2>

      {/* User Information */}
      <div className="settings-section">
        <h3 className="section-title">User Information</h3>
        <div className="info-card">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Username</span>
              <span className="info-value">{user?.username}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Full Name</span>
              <span className="info-value">{user?.full_name}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Role</span>
              <span className="info-value role">{user?.role}</span>
            </div>
            {user?.email && (
              <div className="info-item">
                <span className="info-label">Email</span>
                <span className="info-value">{user.email}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Change Password */}
      <div className="settings-section">
        <h3 className="section-title">Change Password</h3>
        <div className="password-card">
          <div className="form-group">
            <label>Current Password</label>
            <input
              type="password"
              value={passwordForm.old_password}
              onChange={(e) =>
                setPasswordForm({
                  ...passwordForm,
                  old_password: e.target.value,
                })
              }
              className="form-control"
              placeholder="Enter current password"
            />
          </div>
          <div className="form-group">
            <label>New Password</label>
            <input
              type="password"
              value={passwordForm.new_password}
              onChange={(e) =>
                setPasswordForm({
                  ...passwordForm,
                  new_password: e.target.value,
                })
              }
              className="form-control"
              placeholder="Enter new password (min 6 characters)"
            />
          </div>
          <div className="form-group">
            <label>Confirm New Password</label>
            <input
              type="password"
              value={passwordForm.confirm_password}
              onChange={(e) =>
                setPasswordForm({
                  ...passwordForm,
                  confirm_password: e.target.value,
                })
              }
              className="form-control"
              placeholder="Confirm new password"
            />
          </div>
          <button
            onClick={handleChangePassword}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? "Changing Password..." : "Change Password"}
          </button>
        </div>
      </div>
    </div>
  );
}
