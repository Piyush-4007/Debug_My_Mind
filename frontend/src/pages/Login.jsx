import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiError } from "../api/client";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(apiError(err, "Login failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Log in to keep debugging your mind.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Email" type="email" value={email} onChange={setEmail} />
        <Field label="Password" type="password" value={password} onChange={setPassword} />
        {error && <p className="text-sm font-medium text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-lg bg-brand-maroon py-2.5 font-semibold text-white transition hover:bg-brand-pink disabled:opacity-60"
        >
          {busy ? "Logging in…" : "Log in"}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-brand-rose">
        No account?{" "}
        <Link to="/signup" className="font-semibold text-brand-pink hover:underline">
          Sign up
        </Link>
      </p>
      <p className="mt-2 text-center text-xs text-brand-rose/70">
        Demo: student@demo.dev / password
      </p>
    </AuthShell>
  );
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-brand-pink/20 bg-white p-8 shadow-sm">
        <h1 className="font-display text-3xl font-bold text-brand-maroon">DebugMyMind</h1>
        <p className="mt-1 text-lg font-semibold text-brand-ink">{title}</p>
        <p className="mb-6 text-sm text-brand-rose">{subtitle}</p>
        {children}
      </div>
    </div>
  );
}

export function Field({ label, type = "text", value, onChange, ...rest }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-brand-ink">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        className="w-full rounded-lg border border-brand-pink/30 bg-brand-cream px-3 py-2 text-brand-ink outline-none focus:border-brand-pink focus:ring-2 focus:ring-brand-pink/30"
        {...rest}
      />
    </label>
  );
}
