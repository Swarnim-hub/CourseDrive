import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { API_BASE_URL } from "./constants";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});
	api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const authStorage = localStorage.getItem("coursedrive-auth-storage");
      if (authStorage) {
        try {
          const parsed = JSON.parse(authStorage);
          const token = parsed?.state?.accessToken;
          if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (e) {
          console.error("Error parsing stored auth token", e);
        }
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      if (typeof window !== "undefined") {
        const authStorage = localStorage.getItem("coursedrive-auth-storage");
        if (authStorage) {
          try {
            const parsed = JSON.parse(authStorage);
            const refreshToken = parsed?.state?.refreshToken;
            if (refreshToken) {
              const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });
              const newAccessToken = res.data.access_token;
              parsed.state.accessToken = newAccessToken;
              localStorage.setItem("coursedrive-auth-storage", JSON.stringify(parsed));
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
              }
              return api(originalRequest);
            }
          } catch (refreshErr) {
            localStorage.removeItem("coursedrive-auth-storage");
            window.location.href = "/login";
            return Promise.reject(refreshErr);
          }
        }
      }
    }
    return Promise.reject(error);
  }
);
