import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navClass = ({ isActive }) =>
    `rounded-lg px-3 py-1.5 font-medium transition ${
      isActive ? "bg-violet/10 text-violet-bright" : "text-muted hover:text-ink"
    }`;

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="sticky top-0 z-20 border-b border-line/80 bg-bg/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-grad-violet font-display text-sm font-extrabold text-white shadow-lg">
            D
          </span>
          <span className="font-display text-xl font-extrabold tracking-tight">
            Debug<span className="text-gradient">MyMind</span>
          </span>
        </Link>

        {user && (
          <div className="flex items-center gap-3 text-sm">
            <div className="hidden items-center gap-1 sm:flex">
              <NavLink to="/" end className={navClass}>
                Problems
              </NavLink>
              <NavLink to="/dashboard" className={navClass}>
                Dashboard
              </NavLink>
            </div>
            <div className="hidden items-center gap-2 sm:flex">
              <span className="text-muted">{user.name}</span>
              <span className="rounded-full border border-violet/30 bg-violet/10 px-2 py-0.5 text-xs font-semibold capitalize text-violet-bright">
                {user.role}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-line px-3 py-1.5 font-medium text-muted transition hover:border-violet/50 hover:text-ink"
            >
              Log out
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
