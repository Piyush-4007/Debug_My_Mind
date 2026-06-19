import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiError } from "../api/client";
import { AuthShell, Field, ErrorNote, SubmitButton } from "./Login";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "student" });
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
        <Field label="I am a">
          <select
            value={form.role}
            onChange={(e) => set("role")(e.target.value)}
            className="w-full rounded-lg border border-line bg-bg-soft px-3 py-2.5 text-ink outline-none transition focus:border-violet/60 focus:ring-2 focus:ring-violet/25"
          >
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
          </select>
        </Field>
        {error && <ErrorNote>{error}</ErrorNote>}
        <SubmitButton busy={busy}>{busy ? "Creating…" : "Sign up"}</SubmitButton>
      </form>
      <p className="mt-5 text-center text-sm text-muted">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-violet-bright hover:underline">
          Log in
        </Link>
      </p>
    </AuthShell>
  );
}
