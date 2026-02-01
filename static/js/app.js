// Main application JavaScript

let currentUser = null;
let selectedRoomId = null;

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  if (window.location.pathname === "/login") return;

  // Check authentication
  if (!Auth.isAuthenticated()) {
    window.location.href = "/login";
    return;
  }

  currentUser = Auth.getUser();
  initializeApp();
});

function initializeApp() {
  setupEventListeners();
  loadDashboardData();
}

function setupEventListeners() {
  // Initialize date inputs
  initializeDateInputs();

  // Room management
  document
    .getElementById("refresh-rooms")
    ?.addEventListener("click", loadRooms);

  // Reservation management
  document
    .getElementById("refresh-reservations")
    ?.addEventListener("click", loadReservations);

  // New reservation form
  document
    .getElementById("search-rooms")
    ?.addEventListener("click", searchAvailableRooms);
  document
    .getElementById("new-reservation-form")
    ?.addEventListener("submit", createReservation);

  // Room status modal
  const modal = document.getElementById("room-status-modal");
  const closeModal = modal?.querySelectorAll(".close");
  closeModal?.forEach((btn) => {
    btn.addEventListener("click", () => (modal.style.display = "none"));
  });

  document
    .getElementById("room-status-form")
    ?.addEventListener("submit", updateRoomStatus);

  // Close modal when clicking outside
  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}

function switchSection(sectionName) {
  // Update menu
  document.querySelectorAll(".menu-item").forEach((item) => {
    item.classList.remove("active");
  });
  document
    .querySelector(`[data-section="${sectionName}"]`)
    .classList.add("active");

  // Update content
  document.querySelectorAll(".section").forEach((section) => {
    section.classList.remove("active");
  });
  document.getElementById(`${sectionName}-section`).classList.add("active");

  // Load section-specific data
  switch (sectionName) {
    case "dashboard":
      loadDashboardData();
      break;
    case "rooms":
      loadRooms();
      break;
    case "reservations":
      loadReservations();
      break;
    case "new-reservation":
      // Reset form
      document.getElementById("new-reservation-form")?.reset();
      document.getElementById("available-rooms").innerHTML = "";
      selectedRoomId = null;
      break;
  }
}

async function loadDashboardData() {
  try {
    const stats = await Auth.apiRequest("/api/dashboard/stats");
    if (stats.success) {
      document.getElementById("total-rooms").textContent =
        stats.stats.total_rooms;
      document.getElementById("available-rooms").textContent =
        stats.stats.available_rooms;
      document.getElementById("occupied-rooms").textContent =
        stats.stats.occupied_rooms;
      document.getElementById("occupancy-rate").textContent =
        stats.stats.occupancy_rate + "%";
    }
  } catch (error) {
    console.error("Failed to load dashboard data:", error);
    showAlert("Failed to load dashboard data", "error");
  }
}

async function loadRooms() {
  try {
    const roomsGrid = document.getElementById("rooms-grid");
    roomsGrid.innerHTML = '<div class="loading">Loading rooms...</div>';

    const response = await Auth.apiRequest("/api/rooms");
    if (response.success) {
      displayRooms(response.data);
    }
  } catch (error) {
    console.error("Failed to load rooms:", error);
    showAlert("Failed to load rooms", "error");
  }
}

function displayRooms(rooms) {
  const roomsGrid = document.getElementById("rooms-grid");

  if (rooms.length === 0) {
    roomsGrid.innerHTML = "<p>No rooms found.</p>";
    return;
  }

  roomsGrid.innerHTML = rooms
    .map(
      (room) => `
        <div class="room-card">
            <div class="room-header">
                <div class="room-number">Room ${room.room_number}</div>
                <span class="room-status ${room.status.toLowerCase().replace(" ", "-")}">${room.status}</span>
            </div>
            <div class="room-info">
                <p><strong>Type:</strong> ${room.type_name}</p>
                <p><strong>Floor:</strong> ${room.floor}</p>
                <p><strong>Max Occupancy:</strong> ${room.max_occupancy}</p>
                <p><strong>Base Price:</strong> ¥${room.base_price}</p>
            </div>
            ${
              canUpdateRoomStatus()
                ? `
                <div class="room-actions">
                    <button class="btn btn-small btn-secondary" onclick="openRoomStatusModal(${room.room_id}, '${room.room_number}', '${room.status}')">
                        Update Status
                    </button>
                </div>
            `
                : ""
            }
        </div>
    `,
    )
    .join("");
}

function canUpdateRoomStatus() {
  return (
    currentUser &&
    (currentUser.role === "admin" || currentUser.role === "housekeeping")
  );
}

function openRoomStatusModal(roomId, roomNumber, currentStatus) {
  const modal = document.getElementById("room-status-modal");
  document.getElementById("modal-room-id").value = roomId;
  document.getElementById("modal-room-status").value = currentStatus;
  modal.querySelector("h3").textContent = `Update Status - Room ${roomNumber}`;
  modal.style.display = "block";
}

async function updateRoomStatus(e) {
  e.preventDefault();

  const roomId = document.getElementById("modal-room-id").value;
  const status = document.getElementById("modal-room-status").value;

  try {
    const response = await Auth.apiRequest(`/api/rooms/${roomId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    });

    if (response.success) {
      showAlert("Room status updated successfully", "success");
      document.getElementById("room-status-modal").style.display = "none";
      loadRooms(); // Refresh rooms list
    } else {
      showAlert(response.message, "error");
    }
  } catch (error) {
    console.error("Failed to update room status:", error);
    showAlert("Failed to update room status", "error");
  }
}

async function loadReservations() {
  try {
    const tableContainer = document.getElementById("reservations-table");
    tableContainer.innerHTML =
      '<div class="loading">Loading reservations...</div>';

    const response = await Auth.apiRequest("/api/reservations");
    if (response.success) {
      displayReservations(response.data);
    }
  } catch (error) {
    console.error("Failed to load reservations:", error);
    showAlert("Failed to load reservations", "error");
  }
}

function displayReservations(reservations) {
  const tableContainer = document.getElementById("reservations-table");

  if (reservations.length === 0) {
    tableContainer.innerHTML = "<p>No reservations found.</p>";
    return;
  }

  tableContainer.innerHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Guest</th>
                    <th>Room</th>
                    <th>Check-in</th>
                    <th>Check-out</th>
                    <th>Status</th>
                    <th>Total Price</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${reservations
                  .map(
                    (reservation) => `
                    <tr>
                        <td>#${reservation.reservation_id}</td>
                        <td>${reservation.guest_first_name} ${reservation.guest_last_name}</td>
                        <td>Room ${reservation.room_number}</td>
                        <td>${formatDate(reservation.check_in_date)}</td>
                        <td>${formatDate(reservation.check_out_date)}</td>
                        <td><span class="status ${reservation.status.toLowerCase()}">${reservation.status}</span></td>
                        <td>¥${reservation.total_price}</td>
                        <td>
                            ${
                              canCancelReservation(reservation)
                                ? `
                                <button class="btn btn-small btn-secondary" onclick="cancelReservation(${reservation.reservation_id})">
                                    Cancel
                                </button>
                            `
                                : "-"
                            }
                        </td>
                    </tr>
                `,
                  )
                  .join("")}
            </tbody>
        </table>
    `;
}

function canCancelReservation(reservation) {
  return (
    currentUser &&
    (currentUser.role === "admin" || currentUser.role === "front_desk") &&
    reservation.status === "Confirmed"
  );
}

async function cancelReservation(reservationId) {
  if (!confirm("Are you sure you want to cancel this reservation?")) {
    return;
  }

  try {
    const response = await Auth.apiRequest(
      `/api/reservations/${reservationId}`,
      {
        method: "DELETE",
      },
    );

    if (response.success) {
      showAlert("Reservation cancelled successfully", "success");
      loadReservations(); // Refresh reservations list
    } else {
      showAlert(response.message, "error");
    }
  } catch (error) {
    console.error("Failed to cancel reservation:", error);
    showAlert("Failed to cancel reservation", "error");
  }
}

async function searchAvailableRooms() {
  const checkInDate = document.getElementById("check-in-date").value;
  const checkOutDate = document.getElementById("check-out-date").value;

  if (!checkInDate || !checkOutDate) {
    showAlert("Please select both check-in and check-out dates", "error");
    return;
  }

  if (new Date(checkInDate) >= new Date(checkOutDate)) {
    showAlert("Check-out date must be after check-in date", "error");
    return;
  }

  try {
    const availableRoomsContainer = document.getElementById("available-rooms");
    availableRoomsContainer.innerHTML =
      '<div class="loading">Searching available rooms...</div>';

    const response = await Auth.apiRequest(
      `/api/rooms/available?check_in=${checkInDate}&check_out=${checkOutDate}`,
    );
    if (response.success) {
      displayAvailableRooms(response.data, checkInDate, checkOutDate);
    }
  } catch (error) {
    console.error("Failed to search rooms:", error);
    showAlert("Failed to search available rooms", "error");
  }
}

async function displayAvailableRooms(rooms, checkInDate, checkOutDate) {
  const container = document.getElementById("available-rooms");

  if (rooms.length === 0) {
    container.innerHTML = "<p>No rooms available for the selected dates.</p>";
    return;
  }

  // Calculate prices for each room
  const roomsWithPrices = await Promise.all(
    rooms.map(async (room) => {
      try {
        const priceResponse = await Auth.apiRequest(
          `/api/pricing/calculate?room_type_id=${room.room_type_id}&check_in=${checkInDate}&check_out=${checkOutDate}`,
        );
        room.calculated_price = priceResponse.success
          ? priceResponse.price
          : room.base_price;
      } catch (error) {
        room.calculated_price = room.base_price;
      }
      return room;
    }),
  );

  container.innerHTML = roomsWithPrices
    .map(
      (room) => `
        <div class="available-room-card" onclick="selectRoom(${room.room_id}, this)">
            <h4>Room ${room.room_number}</h4>
            <p><strong>Type:</strong> ${room.type_name}</p>
            <p><strong>Max Occupancy:</strong> ${room.max_occupancy}</p>
            <div class="price">¥${room.calculated_price}</div>
        </div>
    `,
    )
    .join("");
}

function selectRoom(roomId, element) {
  // Remove previous selection
  document.querySelectorAll(".available-room-card").forEach((card) => {
    card.classList.remove("selected");
  });

  // Select current room
  element.classList.add("selected");
  selectedRoomId = roomId;
}

async function createReservation(e) {
  e.preventDefault();

  if (!selectedRoomId) {
    showAlert("Please select a room first", "error");
    return;
  }

  const formData = new FormData(e.target);
  const guestInfo = {
    first_name: formData.get("first_name"),
    last_name: formData.get("last_name"),
    email: formData.get("email"),
    phone: formData.get("phone"),
  };

  const reservationData = {
    guest_info: guestInfo,
    room_id: selectedRoomId,
    check_in_date: formData.get("check_in_date"),
    check_out_date: formData.get("check_out_date"),
    num_guests: parseInt(formData.get("num_guests")),
    special_requests: formData.get("special_requests") || "",
  };

  try {
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = "Creating Reservation...";

    const response = await Auth.apiRequest("/api/reservations", {
      method: "POST",
      body: JSON.stringify(reservationData),
    });

    if (response.success) {
      showAlert(
        `Reservation created successfully! Reservation ID: #${response.reservation_id}`,
        "success",
      );
      e.target.reset();
      document.getElementById("available-rooms").innerHTML = "";
      selectedRoomId = null;

      // Switch to reservations view
      setTimeout(() => {
        switchSection("reservations");
      }, 2000);
    } else {
      showAlert(response.message, "error");
    }
  } catch (error) {
    console.error("Failed to create reservation:", error);
    showAlert("Failed to create reservation", "error");
  } finally {
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = false;
    submitButton.textContent = "Create Reservation";
  }
}

// Utility functions
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function showAlert(message, type = "info") {
  // Remove existing alerts
  const existingAlerts = document.querySelectorAll(".alert");
  existingAlerts.forEach((alert) => alert.remove());

  // Create new alert
  const alert = document.createElement("div");
  alert.className = `alert alert-${type}`;
  alert.textContent = message;

  // Insert at top of content area
  const content = document.querySelector(".content");
  content.insertBefore(alert, content.firstChild);

  // Auto remove after 5 seconds
  setTimeout(() => {
    alert.remove();
  }, 5000);

  // Scroll to top to show the alert
  content.scrollTop = 0;
}
function initializeDateInputs() {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const checkInInput = document.getElementById("check-in-date");
  const checkOutInput = document.getElementById("check-out-date");

  if (checkInInput) {
    checkInInput.setAttribute("min", today.toISOString().split("T")[0]);
    checkInInput.addEventListener("change", function () {
      if (checkOutInput) {
        const selectedDate = new Date(this.value);
        const minCheckOut = new Date(selectedDate);
        minCheckOut.setDate(minCheckOut.getDate() + 1);
        checkOutInput.setAttribute(
          "min",
          minCheckOut.toISOString().split("T")[0],
        );

        if (
          checkOutInput.value &&
          new Date(checkOutInput.value) <= selectedDate
        ) {
          checkOutInput.value = minCheckOut.toISOString().split("T")[0];
        }
      }
    });
  }

  if (checkOutInput) {
    checkOutInput.setAttribute("min", tomorrow.toISOString().split("T")[0]);
  }
}
