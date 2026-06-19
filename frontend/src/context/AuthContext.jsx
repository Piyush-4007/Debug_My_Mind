import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("dmm_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [loading, setLoading] = useState(true);

  // Validate any stored token on first load.
  useEffect(() => {
    const token = localStorage.getItem("dmm_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/api/auth/me")
      .then((res) => persist(token, res.data.user))
      .catch(() => persist(null, null))
      .finally(() => setLoading(false));
  }, []);

  function persist(token, nextUser) {
    if (token) localStorage.setItem("dmm_token", token);
    else localStorage.removeItem("dmm_token");
    if (nextUser) localStorage.setItem("dmm_user", JSON.stringify(nextUser));
    else localStorage.removeItem("dmm_user");
    setUser(nextUser);
  }

  async function login(email, password) {
    const res = await api.post("/api/auth/login", { email, password });
    persist(res.data.token, res.data.user);
    return res.data.user;
  }

  async function signup(payload) {
    const res = await api.post("/api/auth/signup", payload);
    persist(res.data.token, res.data.user);
    return res.data.user;
  }

  function logout() {
    persist(null, null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
