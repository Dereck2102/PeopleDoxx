import { NavLink, useNavigate } from 'react-router-dom';
import { logout, getStoredEmail } from '@/lib/api';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const email = getStoredEmail() ?? 'admin';

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="flex min-h-screen bg-slate-900">
      {/* Sidebar */}
      <aside className="flex w-60 flex-shrink-0 flex-col bg-slate-950 border-r border-slate-800">
        {/* Logo */}
        <div className="flex items-center gap-2 px-5 py-5 border-b border-slate-800">
          <span className="flex h-6 w-6 items-center justify-center rounded bg-orange-500 font-bold text-slate-900 text-xs">
            PD
          </span>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-bold text-white">PeopleDoxx</span>
            <span className="text-xs text-slate-400">Admin Panel</span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-orange-500 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/users"
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-orange-500 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            Usuarios
          </NavLink>
        </nav>

        {/* Footer */}
        <div className="border-t border-slate-800 px-4 py-4">
          <p className="text-xs text-slate-400 truncate mb-2">{email}</p>
          <button
            onClick={handleLogout}
            className="w-full rounded-lg bg-slate-800 px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors text-left"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
