"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthService } from "../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!username || !password) {
      setError("Please enter both username and password");
      return;
    }

    setLoading(true);
    try {
      const response = await AuthService.login(username, password);
      if (response.success && response.session_token && response.user) {
        AuthService.setToken(response.session_token);
        AuthService.setUser(response.user);
        router.push("/dashboard");
      } else {
        setError(response.message || "Login failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fillDemoAccount = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="logo">
          <div className="logo-icon">H</div>
          <h1>HRMS</h1>
          <p>Hotel Reservation Management System</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        {error && (
          <div className="alert alert-error" style={{ marginTop: "1rem" }}>
            {error}
          </div>
        )}

        <div className="demo-accounts">
          <h3>Demo Accounts:</h3>
          <div className="account-grid">
            <div
              className="account-item"
              onClick={() => fillDemoAccount("admin", "admin123")}
            >
              <strong>Administrator</strong>
              <span>admin / admin123</span>
            </div>
            <div
              className="account-item"
              onClick={() => fillDemoAccount("frontdesk", "front123")}
            >
              <strong>Front Desk</strong>
              <span>frontdesk / front123</span>
            </div>
            <div
              className="account-item"
              onClick={() => fillDemoAccount("housekeeping", "house123")}
            >
              <strong>Housekeeping</strong>
              <span>housekeeping / house123</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
