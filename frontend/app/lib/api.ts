import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Format date to yyyy-mm-dd
export function formatDate(date: Date | string): string {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

// Format datetime to yyyy-mm-dd hh:mm:ss
export function formatDateTime(date: Date | string): string {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// Add axios interceptor for handling 401 errors globally
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== "undefined") {
        localStorage.removeItem("session_token");
        localStorage.removeItem("user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

export interface User {
  user_id: number;
  username: string;
  role: string;
  full_name: string;
  email?: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  session_token?: string;
  user?: User;
}

export interface Room {
  room_id: number;
  room_number: string;
  room_type_id: number;
  type_name: string;
  floor: number;
  status: string;
  base_price: number;
  max_occupancy: number;
  description?: string;
  has_reservation?: boolean; // 是否有预订
  reservation_check_in?: string; // 预订入住日期
}

export interface Reservation {
  reservation_id: number;
  guest_first_name: string;
  guest_last_name: string;
  guest_email?: string;
  guest_phone?: string;
  room_number: string;
  room_type?: string;
  check_in_date: string;
  check_out_date: string;
  status: string;
  total_price: number;
  num_guests?: number;
  special_requests?: string;
  created_at?: string;
}

export interface ReservationDetail extends Reservation {
  guest_name: string;
  phone: string;
  email?: string;
  floor?: number;
  created_by_name?: string;
}

export interface RoomType {
  room_type_id: number;
  type_name: string;
  description: string;
  base_price: number;
  max_occupancy: number;
  amenities: string;
}

export interface SeasonalPricing {
  pricing_id: number;
  room_type_id: number;
  type_name: string;
  season_name: string;
  start_date: string;
  end_date: string;
  price_multiplier?: number;
  fixed_price?: number;
}

export interface OccupancyReport {
  start_date: string;
  end_date: string;
  total_rooms: number;
  days: number;
  average_occupancy_rate: number;
  daily_data: Array<{
    date: string;
    total_rooms: number;
    occupied_rooms: number;
    available_rooms: number;
    occupancy_rate: number;
  }>;
}

export interface RevenueReport {
  start_date: string;
  end_date: string;
  total_reservations: number;
  total_revenue: number;
  average_revenue_per_reservation: number;
  by_room_type: Array<{
    room_type: string;
    reservations: number;
    revenue: number;
  }>;
  by_payment_method: Array<{
    payment_method: string;
    count: number;
    amount: number;
  }>;
}

export interface AuditLog {
  audit_id: number;
  timestamp: string;
  username: string;
  operation_type: string;
  table_name: string;
  record_id?: number;
  description?: string;
}

export interface Backup {
  backup_id: number;
  backup_file: string;
  backup_size: number;
  backup_type: string;
  status: string;
  username: string;
  created_at: string;
}

export interface DashboardStats {
  total_rooms: number;
  occupied_rooms: number;
  reserved_rooms: number;
  available_rooms: number;
  total_reservations: number;
  active_reservations: number;
  today_checkins: number;
  occupancy_rate: number;
}

class AuthService {
  private static TOKEN_KEY = "session_token";
  private static USER_KEY = "user_info";

  static getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static setToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  static getUser(): User | null {
    if (typeof window === "undefined") return null;
    const userInfo = localStorage.getItem(this.USER_KEY);
    return userInfo ? JSON.parse(userInfo) : null;
  }

  static setUser(user: User): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  static removeToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }

  static async login(
    username: string,
    password: string,
  ): Promise<LoginResponse> {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      username,
      password,
    });
    return response.data;
  }

  static async logout(): Promise<void> {
    const token = this.getToken();
    if (token) {
      try {
        await axios.post(
          `${API_BASE_URL}/api/auth/logout`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );
      } catch (error) {
        console.error("Logout error:", error);
      }
    }
    this.removeToken();
  }
}

class ApiService {
  private static getHeaders() {
    const token = AuthService.getToken();
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  static async getDashboardStats(): Promise<DashboardStats> {
    const response = await axios.get(`${API_BASE_URL}/api/dashboard/stats`, {
      headers: this.getHeaders(),
    });
    return response.data.stats;
  }

  static async getRooms(): Promise<Room[]> {
    const response = await axios.get(`${API_BASE_URL}/api/rooms`, {
      headers: this.getHeaders(),
    });
    return response.data.data;
  }

  static async getRoomsWithReservations(): Promise<Room[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/rooms/with-reservations`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async getAvailableRooms(
    checkIn: string,
    checkOut: string,
  ): Promise<Room[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/rooms/available?check_in=${checkIn}&check_out=${checkOut}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async updateRoomStatus(roomId: number, status: string): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}/api/rooms/${roomId}/status`,
      { status },
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async getReservations(): Promise<Reservation[]> {
    const response = await axios.get(`${API_BASE_URL}/api/reservations`, {
      headers: this.getHeaders(),
    });
    return response.data.data;
  }

  static async createReservation(data: any): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/reservations`,
      data,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async cancelReservation(reservationId: number): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}/api/reservations/${reservationId}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async calculatePrice(
    roomTypeId: number,
    checkIn: string,
    checkOut: string,
  ): Promise<number> {
    const response = await axios.get(
      `${API_BASE_URL}/api/pricing/calculate?room_type_id=${roomTypeId}&check_in=${checkIn}&check_out=${checkOut}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.price;
  }

  // ==================== Extended Reservation APIs ====================

  static async searchReservations(criteria: {
    guest_name?: string;
    phone?: string;
    reservation_id?: number;
    room_number?: string;
  }): Promise<ReservationDetail[]> {
    const response = await axios.post(
      `${API_BASE_URL}/api/reservations/search`,
      criteria,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async getReservationDetail(
    reservationId: number,
  ): Promise<ReservationDetail> {
    const response = await axios.get(
      `${API_BASE_URL}/api/reservations/${reservationId}/detail`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async updateReservation(
    reservationId: number,
    data: {
      check_in_date?: string;
      check_out_date?: string;
      num_guests?: number;
      special_requests?: string;
    },
  ): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}/api/reservations/${reservationId}`,
      data,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async checkIn(reservationId: number): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/reservations/${reservationId}/check-in`,
      {},
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async checkOut(
    reservationId: number,
    paymentMethod: string,
    paymentAmount: number,
  ): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/reservations/${reservationId}/check-out`,
      {
        reservation_id: reservationId,
        payment_method: paymentMethod,
        payment_amount: paymentAmount,
      },
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async getTodayCheckins(): Promise<ReservationDetail[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/reservations/today-checkins`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async getCurrentGuests(): Promise<ReservationDetail[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/reservations/current-guests`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  // ==================== Room Type Management APIs ====================

  static async getRoomTypes(): Promise<RoomType[]> {
    const response = await axios.get(`${API_BASE_URL}/api/room-types`, {
      headers: this.getHeaders(),
    });
    return response.data.data;
  }

  static async getRoomTypeDetail(roomTypeId: number): Promise<RoomType> {
    const response = await axios.get(
      `${API_BASE_URL}/api/room-types/${roomTypeId}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async addRoomType(data: {
    type_name: string;
    description: string;
    base_price: number;
    max_occupancy: number;
    amenities: string;
  }): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/api/room-types`, data, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  static async updateRoomType(
    roomTypeId: number,
    data: {
      type_name?: string;
      description?: string;
      base_price?: number;
      max_occupancy?: number;
      amenities?: string;
    },
  ): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}/api/room-types/${roomTypeId}`,
      data,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  // ==================== Room Management APIs ====================

  static async addRoom(data: {
    room_number: string;
    room_type_id: number;
    floor: number;
  }): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/api/rooms`, data, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  static async getRoomStatistics(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/api/rooms/statistics`, {
      headers: this.getHeaders(),
    });
    return response.data.data;
  }

  // ==================== Pricing Management APIs ====================

  static async getSeasonalPricing(): Promise<SeasonalPricing[]> {
    const response = await axios.get(`${API_BASE_URL}/api/pricing/seasonal`, {
      headers: this.getHeaders(),
    });
    return response.data.data;
  }

  static async addSeasonalPricing(data: {
    room_type_id: number;
    season_name: string;
    start_date: string;
    end_date: string;
    price_multiplier?: number;
    fixed_price?: number;
  }): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/pricing/seasonal`,
      data,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async deleteSeasonalPricing(pricingId: number): Promise<any> {
    const response = await axios.delete(
      `${API_BASE_URL}/api/pricing/seasonal/${pricingId}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  // ==================== Report APIs ====================

  static async getOccupancyReport(
    startDate: string,
    endDate: string,
  ): Promise<OccupancyReport> {
    const response = await axios.get(
      `${API_BASE_URL}/api/reports/occupancy?start_date=${startDate}&end_date=${endDate}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async getRevenueReport(
    startDate: string,
    endDate: string,
  ): Promise<RevenueReport> {
    const response = await axios.get(
      `${API_BASE_URL}/api/reports/revenue?start_date=${startDate}&end_date=${endDate}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async getAuditLogs(params: {
    operation_type?: string;
    table_name?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<AuditLog[]> {
    const queryParams = new URLSearchParams();
    if (params.operation_type)
      queryParams.append("operation_type", params.operation_type);
    if (params.table_name) queryParams.append("table_name", params.table_name);
    if (params.start_date) queryParams.append("start_date", params.start_date);
    if (params.end_date) queryParams.append("end_date", params.end_date);
    if (params.limit) queryParams.append("limit", params.limit.toString());

    const response = await axios.get(
      `${API_BASE_URL}/api/audit-logs?${queryParams.toString()}`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async createBackup(backupName: string = "hrms_backup"): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/backup?backup_name=${backupName}`,
      {},
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }

  static async getBackupHistory(): Promise<Backup[]> {
    const response = await axios.get(`${API_BASE_URL}/api/backups`, {
      headers: this.getHeaders(),
    });
    return response.data.data;
  }

  // ==================== Check-in/Check-out Helper APIs ====================

  static async getTodayCheckins(): Promise<any[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/reservations/today-checkins`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  static async getCurrentGuests(): Promise<any[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/reservations/current-guests`,
      {
        headers: this.getHeaders(),
      },
    );
    return response.data.data;
  }

  // ==================== User Management APIs ====================

  static async changePassword(
    userId: number,
    oldPassword: string,
    newPassword: string,
  ): Promise<any> {
    const response = await axios.put(
      `${API_BASE_URL}/api/users/${userId}/password`,
      {
        old_password: oldPassword,
        new_password: newPassword,
      },
      {
        headers: this.getHeaders(),
      },
    );
    return response.data;
  }
}

export { AuthService, ApiService };
