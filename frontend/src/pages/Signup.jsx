import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiError } from "../api/client";
import { AuthShell, Field } from "./Login";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (key) => (val) => setForm((f) => ({ ...f, [key]: val }));

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await signup(form);
      navigate("/");
    } catch (err) {
      setError(apiError(err, "Signup failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="Start learning from your mistakes.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Name" value={form.name} onChange={set("name")} />
        <Field label="Email" type="email" value={form.email} onChange={set("email")} />
        <Field
          label="Password"
          type="password"
          value={form.password}
          onChange={set("password")}
          minLength={6}
        />
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-brand-ink">I am a</span>
          <select
            value={form.role}
            onChange={(e) => set("role")(e.target.value)}
            className="w-full rounded-lg border border-brand-pink/30 bg-brand-cream px-3 py-2 text-brand-ink outline-none focus:border-brand-pink focus:ring-2 focus:ring-brand-pink/30"
          >
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
          </select>
        </label>
        {error && <p className="text-sm font-medium text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-lg bg-brand-maroon py-2.5 font-semibold text-white transition hover:bg-brand-pink disabled:opacity-60"
        >
          {busy ? "Creating…" : "Sign up"}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-brand-rose">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-brand-pink hover:underline">
          Log in
        </Link>
      </p>
    </AuthShell>
  );
}
