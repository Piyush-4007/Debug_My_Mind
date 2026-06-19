import axios from "axios";

// In dev, leave VITE_API_URL empty: requests go to the same origin (:5173)
// and the Vite proxy forwards /api/* to the backend.
// In prod (Vercel), set VITE_API_URL to the absolute Render backend URL.
const baseURL = import.meta.env.VITE_API_URL || "";

const api = axios.create({ baseURL });

// Attach the JWT (if any) to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("dmm_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, clear the stale token so the app falls back to the login screen.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("dmm_token");
      localStorage.removeItem("dmm_user");
    }
    return Promise.reject(err);
  }
);

/**
 * Turn an axios error into a human-readable message.
 * Distinguishes "server said no" (has a response) from "couldn't reach server".
 */
export function apiError(err, fallback = "Something went wrong") {
  if (err.response?.data?.error) return err.response.data.error;
  if (err.code === "ERR_NETWORK" || err.request) {
    return "Cannot reach the server. Is the backend running on :5000? Please try again.";
  }
  return err.message || fallback;
}

export default api;
