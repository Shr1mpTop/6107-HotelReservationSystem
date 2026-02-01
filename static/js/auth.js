// Authentication utilities
class Auth {
  static getToken() {
    return localStorage.getItem("session_token");
  }

  static setToken(token) {
    localStorage.setItem("session_token", token);
  }

  static setUser(user) {
    localStorage.setItem("user_info", JSON.stringify(user));
  }

  static getUser() {
    const userInfo = localStorage.getItem("user_info");
    return userInfo ? JSON.parse(userInfo) : null;
  }

  static removeToken() {
    localStorage.removeItem("session_token");
    localStorage.removeItem("user_info");
  }

  static isAuthenticated() {
    return !!this.getToken();
  }

  static async apiRequest(url, options = {}) {
    const token = this.getToken();

    const config = {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        this.removeToken();
        window.location.href = "/login";
        return null;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || `HTTP error! status: ${response.status}`,
        );
      }

      return data;
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }
}

// Login page functionality
if (window.location.pathname === "/login") {
  document.addEventListener("DOMContentLoaded", function () {
    // Check if already authenticated
    if (Auth.isAuthenticated()) {
      window.location.href = "/";
      return;
    }

    const loginForm = document.getElementById("loginForm");
    const errorMessage = document.getElementById("error-message");

    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;

      if (!username || !password) {
        showError("Please enter both username and password");
        return;
      }

      try {
        const submitButton = loginForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = "Logging in...";

        const response = await Auth.apiRequest("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({ username, password }),
        });

        if (response.success) {
          Auth.setToken(response.session_token);
          Auth.setUser(response.user);
          window.location.href = "/";
        } else {
          showError(response.message);
        }
      } catch (error) {
        showError("Login failed: " + error.message);
      } finally {
        const submitButton = loginForm.querySelector('button[type="submit"]');
        submitButton.disabled = false;
        submitButton.textContent = "Login";
      }
    });

    function showError(message) {
      errorMessage.textContent = message;
      errorMessage.style.display = "block";
      setTimeout(() => {
        errorMessage.style.display = "none";
      }, 5000);
    }

    // Demo account quick login
    document.querySelectorAll(".account-item").forEach((item) => {
      item.addEventListener("click", function () {
        const credentials = this.querySelector("span").textContent.split(" / ");
        document.getElementById("username").value = credentials[0];
        document.getElementById("password").value = credentials[1];
      });
    });
  });
}

// Dashboard page functionality
if (window.location.pathname === "/" || window.location.pathname === "") {
  document.addEventListener("DOMContentLoaded", function () {
    // Check authentication
    if (!Auth.isAuthenticated()) {
      window.location.href = "/login";
      return;
    }

    // Initialize dashboard
    initializeDashboard();
  });
}

function initializeDashboard() {
  const user = Auth.getUser();
  if (user) {
    document.getElementById("user-info").textContent =
      `${user.full_name} (${user.role})`;
  }

  // Logout functionality
  document
    .getElementById("logout-btn")
    .addEventListener("click", async function () {
      try {
        await Auth.apiRequest("/api/auth/logout", { method: "POST" });
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        Auth.removeToken();
        window.location.href = "/login";
      }
    });

  // Navigation functionality
  document.querySelectorAll(".menu-item").forEach((item) => {
    item.addEventListener("click", function () {
      const section = this.dataset.section;
      switchSection(section);
    });
  });

  // Load initial dashboard data
  loadDashboardData();
}
