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
        {error && <ErrorNote>{error}</ErrorNote>}
        <SubmitButton busy={busy}>{busy ? "Logging in…" : "Log in"}</SubmitButton>
      </form>
      <p className="mt-5 text-center text-sm text-muted">
        No account?{" "}
        <Link to="/signup" className="font-semibold text-violet-bright hover:underline">
          Sign up
        </Link>
      </p>
      <p className="mt-2 text-center text-xs text-faint">
        Demo: student@demo.dev · password
      </p>
    </AuthShell>
  );
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="animate-rise w-full max-w-md">
        <div className="mb-6 text-center">
          <span className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-xl bg-grad-violet font-display text-lg font-extrabold text-white glow-violet">
            D
          </span>
          <h1 className="font-display text-3xl font-extrabold tracking-tight">
            Debug<span className="text-gradient">MyMind</span>
          </h1>
        </div>
        <div className="card p-8">
          <p className="text-lg font-semibold text-ink">{title}</p>
          <p className="mb-6 text-sm text-muted">{subtitle}</p>
          {children}
        </div>
      </div>
    </div>
  );
}

export function Field({ label, type = "text", value, onChange, children, ...rest }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-muted">{label}</span>
      {children || (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required
          className="w-full rounded-lg border border-line bg-bg-soft px-3 py-2.5 text-ink outline-none transition focus:border-violet/60 focus:ring-2 focus:ring-violet/25"
          {...rest}
        />
      )}
    </label>
  );
}

export function ErrorNote({ children }) {
  return (
    <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm font-medium text-red-300">
      {children}
    </p>
  );
}

export function SubmitButton({ busy, children }) {
  return (
    <button
      type="submit"
      disabled={busy}
      className="w-full rounded-lg bg-grad-violet py-2.5 font-semibold text-white shadow-lg transition hover:opacity-95 hover:glow-violet disabled:opacity-60"
    >
      {children}
    </button>
  );
}
