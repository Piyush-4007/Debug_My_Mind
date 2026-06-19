import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="border-b-2 border-brand-pink/30 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link to="/" className="font-display text-2xl font-bold text-brand-maroon">
          DebugMyMind
        </Link>
        {user && (
          <div className="flex items-center gap-4 text-sm">
            <span className="text-brand-rose">
              {user.name}
              <span className="ml-2 rounded-full bg-brand-pink/10 px-2 py-0.5 text-xs font-semibold text-brand-pink">
                {user.role}
              </span>
            </span>
            <button
              onClick={handleLogout}
              className="rounded-md border border-brand-pink px-3 py-1 font-medium text-brand-pink transition hover:bg-brand-pink hover:text-white"
            >
              Log out
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
