const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { token, ...fetchOptions } = options;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async login(email: string, password: string) {
    return this.request<{ access_token: string; refresh_token: string }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async getDashboardStats(token: string) {
    return this.request("/api/v1/dashboard/stats", { token });
  }

  async getCameras(token: string, page = 1) {
    return this.request(`/api/v1/cameras?page=${page}`, { token });
  }

  async getViolations(token: string, page = 1) {
    return this.request(`/api/v1/violations?page=${page}`, { token });
  }

  async getAlerts(token: string, page = 1) {
    return this.request(`/api/v1/alerts?page=${page}`, { token });
  }
}

export const api = new ApiClient(API_URL);
