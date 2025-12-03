import { Outlet, Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faThLarge,
  faCog,
  faTicket,
  faUsers,
  faLink,
  faTerminal,
  faDatabase,
  faServer,
  faChartBar,
  faSignOutAlt,
  faBars,
  faRobot,
  faClock,
  faUser,
  faInfoCircle,
  faCodeBranch,
  faSpinner,
  faCheck,
  faArrowUp,
  faExclamationTriangle,
} from "@fortawesome/free-solid-svg-icons";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: faThLarge },
  { name: "Services", href: "/services", icon: faServer },
  { name: "Tickets", href: "/tickets", icon: faTicket },
  { name: "Invites", href: "/invites", icon: faLink },
  { name: "Members", href: "/members", icon: faUsers },
  { name: "Commands", href: "/commands", icon: faTerminal },
  { name: "Guild Stats", href: "/guild-stats", icon: faChartBar },
  { name: "Databases", href: "/databases", icon: faDatabase },
];

const secondaryNav = [
  { name: "Settings", href: "/settings", icon: faCog },
  { name: "About", href: "/about", icon: faInfoCircle },
];

export default function Layout() {
  const { user, logout, authEnabled } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [botStatus, setBotStatus] = useState({ online: false });
  const [versionInfo, setVersionInfo] = useState<{
    local: string;
    remote: string;
    is_update_available: boolean;
    error?: string;
    checking: boolean;
  }>({
    local: "unknown",
    remote: "unknown",
    is_update_available: false,
    checking: false,
  });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Fetch bot status
    const fetchBotStatus = async () => {
      try {
        const response = await api.get("/dashboard/bot-status");
        if (response.data) {
          setBotStatus(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch bot status:", error);
      }
    };

    fetchBotStatus();
    // Refresh bot status every 30 seconds
    const interval = setInterval(fetchBotStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Check version on load
    checkVersion();
  }, []);

  const checkVersion = async () => {
    setVersionInfo((prev) => ({ ...prev, checking: true }));
    try {
      const response = await api.get("/about/version");
      if (response.data) {
        setVersionInfo({
          local: response.data.local,
          remote: response.data.remote,
          is_update_available: response.data.is_update_available,
          error: response.data.error,
          checking: false,
        });
      }
    } catch (error) {
      console.error("Failed to fetch version:", error);
      setVersionInfo((prev) => ({
        ...prev,
        error: "Failed to check version",
        checking: false,
      }));
    }
  };

  const getBadgeContent = () => {
    if (versionInfo.checking) {
      return {
        className: "version-badge badge-info",
        icon: faSpinner,
        text: "",
        title: "Checking for updates...",
        spin: true,
      };
    }
    if (versionInfo.error) {
      return {
        className: "version-badge badge-warning",
        icon: faExclamationTriangle,
        text: "",
        title: "Could not check for updates",
        spin: false,
      };
    }
    if (versionInfo.is_update_available) {
      return {
        className: "version-badge badge-warning",
        icon: faArrowUp,
        text: "Update",
        title: `Update available: v${versionInfo.remote}`,
        spin: false,
        clickable: true,
      };
    }
    return {
      className: "version-badge badge-success",
      icon: faCheck,
      text: "Up to date",
      title: "You are running the latest version",
      spin: false,
    };
  };

  const handleBadgeClick = () => {
    const badge = getBadgeContent();
    if (badge.clickable) {
      window.open(
        "https://github.com/cyb3rgh05t/discord-bot/releases/latest",
        "_blank"
      );
    }
  };

  return (
    <div className="min-h-screen">
      {/* Top Navbar */}
      <nav className="navbar">
        <div className="navbar-container">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 text-text hover:bg-white/10 rounded transition-colors"
            >
              <FontAwesomeIcon icon={faBars} className="w-5 h-5" />
            </button>
            <Link to="/dashboard" className="navbar-brand">
              <FontAwesomeIcon icon={faRobot} className="w-6 h-6 text-accent" />
              <span>Discord Bot Manager</span>
            </Link>
            <div className="bot-status-indicator">
              <span
                className={cn(
                  "status-dot",
                  botStatus.online ? "online" : "offline"
                )}
              ></span>
              <span className="text-sm text-text-muted">
                {botStatus.online ? "Online" : "Offline"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-text-muted text-sm">
              <FontAwesomeIcon icon={faClock} className="w-4 h-4" />
              <span>{currentTime.toLocaleTimeString()}</span>
            </div>

            {authEnabled && user && (
              <div className="flex items-center gap-3 px-3 py-2 rounded hover:bg-white/10 transition-colors">
                <FontAwesomeIcon
                  icon={faUser}
                  className="w-4 h-4 text-text-muted"
                />
                <span className="text-sm text-text">{user.username}</span>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/70 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={cn("sidebar", sidebarOpen && "open")}>
        <div className="sidebar-content">
          <nav className="sidebar-nav">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn("nav-item", isActive && "active")}
                >
                  <FontAwesomeIcon icon={item.icon} className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}

            <div className="nav-divider"></div>

            {secondaryNav.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn("nav-item", isActive && "active")}
                >
                  <FontAwesomeIcon icon={item.icon} className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Sidebar Footer */}
          <div className="sidebar-footer">
            <div
              className="version-info"
              onClick={checkVersion}
              style={{ cursor: "pointer" }}
              title="Click to check for updates"
            >
              <FontAwesomeIcon icon={faCodeBranch} />
              <span>
                Version: <span id="botVersion">{versionInfo.local}</span>
              </span>
              {!versionInfo.checking && (
                <span
                  className={getBadgeContent().className}
                  onClick={handleBadgeClick}
                  title={getBadgeContent().title}
                  style={{
                    cursor: getBadgeContent().clickable ? "pointer" : "default",
                  }}
                >
                  <FontAwesomeIcon
                    icon={getBadgeContent().icon}
                    spin={getBadgeContent().spin}
                  />
                  {getBadgeContent().text && (
                    <span className="ml-1">{getBadgeContent().text}</span>
                  )}
                </span>
              )}
            </div>
            {authEnabled && user && (
              <button
                onClick={logout}
                className="mt-3 w-full flex items-center gap-2 px-4 py-2 text-text-muted hover:text-text hover:bg-white/10 rounded transition-colors text-sm"
              >
                <FontAwesomeIcon icon={faSignOutAlt} className="w-4 h-4" />
                <span>Logout</span>
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <div className="content-wrapper">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
