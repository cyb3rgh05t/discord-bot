import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCog,
  faGlobe,
  faLock,
  faRobot,
  faHashtag,
  faShieldAlt,
  faFilm,
  faFileAlt,
  faSave,
  faSyncAlt,
  faUndo,
  faTimes,
  faCheckCircle,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import api from "@/lib/api";

interface SettingsData {
  values: { [key: string]: string };
  comments: { [key: string]: string };
}

export default function Settings() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<{ [key: string]: string }>({});
  const [comments, setComments] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState<{
    show: boolean;
    message: string;
    type: "success" | "error";
  }>({ show: false, message: "", type: "success" });
  const [autoSave, setAutoSave] = useState(true);
  const [restarting, setRestarting] = useState(false);
  const autoSaveTimeout = useRef<number | null>(null);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await api.get<SettingsData>("/settings/");
        setSettings(response.data.values);
        setComments(response.data.comments);
      } catch (error) {
        console.error("Failed to fetch settings:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const updateSetting = (key: string, value: string | boolean) => {
    // Convert boolean to "True"/"False" string to match Python format
    const stringValue =
      typeof value === "boolean" ? (value ? "True" : "False") : value;

    setSettings((prev) => {
      const updated = { ...prev, [key]: stringValue };

      // Trigger auto-save with updated settings
      if (autoSave) {
        if (autoSaveTimeout.current) {
          clearTimeout(autoSaveTimeout.current);
        }
        autoSaveTimeout.current = window.setTimeout(() => {
          // Save with the updated settings
          api
            .post("/settings", { settings: updated })
            .then(() => {
              setSaveStatus({
                show: true,
                message: "Auto-saved",
                type: "success",
              });
              setTimeout(() => {
                setSaveStatus({ show: false, message: "", type: "success" });
              }, 3000);
            })
            .catch((error: any) => {
              setSaveStatus({
                show: true,
                message:
                  error.response?.data?.detail || "Failed to save settings",
                type: "error",
              });
            });
        }, 5000);
      }

      return updated;
    });
  };

  const handleSave = async (isAutoSave = false) => {
    try {
      const response = await api.post("/settings/", { settings });

      setSaveStatus({
        show: true,
        message: isAutoSave ? "Auto-saved" : response.data.message,
        type: "success",
      });

      setTimeout(() => {
        setSaveStatus({ show: false, message: "", type: "success" });
      }, 3000);
    } catch (error: any) {
      setSaveStatus({
        show: true,
        message: error.response?.data?.detail || "Failed to save settings",
        type: "error",
      });
    }
  };

  const handleSaveAndRestart = async () => {
    try {
      await api.post("/settings/", { settings });
      const response = await api.post("/settings/restart-bot");

      setSaveStatus({
        show: true,
        message: response.data.message || "Restarting bot...",
        type: "success",
      });
      setRestarting(true);

      // Poll health endpoint until bot_ready is true
      const start = Date.now();
      const timeoutMs = 60000; // 60s max
      const pollIntervalMs = 1500;

      const pollHealth = async () => {
        try {
          const health = await api.get("/about/health");
          const ready = Boolean(health?.data?.bot_ready);
          if (ready) {
            setSaveStatus({
              show: true,
              message: "Restart complete.",
              type: "success",
            });
            setRestarting(false);
            setTimeout(() => {
              setSaveStatus({ show: false, message: "", type: "success" });
              window.location.reload();
            }, 1500);
            return;
          }
        } catch (e) {
          // ignore while restarting
        }

        if (Date.now() - start < timeoutMs) {
          setTimeout(pollHealth, pollIntervalMs);
        } else {
          setSaveStatus({
            show: true,
            message: "Restart timed out. Try manual refresh.",
            type: "error",
          });
          setRestarting(false);
        }
      };

      setTimeout(pollHealth, pollIntervalMs);
    } catch (error: any) {
      setSaveStatus({
        show: true,
        message: error.response?.data?.detail || "Failed to restart bot",
        type: "error",
      });
      setRestarting(false);
    }
  };

  const handleReset = () => {
    window.location.reload();
  };

  if (loading) {
    return <LoadingSpinner message="Loading settings..." />;
  }

  return (
    <div className="settings-page">
      {/* Save Status Indicator */}
      {saveStatus.show && (
        <div className={`save-status save-status-${saveStatus.type}`}>
          <FontAwesomeIcon
            icon={
              saveStatus.type === "success"
                ? faCheckCircle
                : faExclamationCircle
            }
          />{" "}
          {saveStatus.message}
        </div>
      )}

      <div className="page-header">
        <div>
          <h1>
            <FontAwesomeIcon icon={faCog} /> Bot Settings
          </h1>
          <p className="subtitle">Configure your Discord bot settings</p>
        </div>
      </div>

      {/* Actions Bar */}
      <div className="actions-bar">
        {restarting && (
          <div className="mb-3 bg-yellow-100 border border-yellow-300 text-yellow-800 px-3 py-2 rounded">
            <FontAwesomeIcon icon={faSyncAlt} /> Restarting bot… waiting for
            health check
          </div>
        )}
        <div className="autosave-toggle">
          <label className="toggle-switch-inline">
            <input
              type="checkbox"
              checked={autoSave}
              onChange={(e) => setAutoSave(e.target.checked)}
            />
            <span className="toggle-slider-inline"></span>
          </label>
          <span className="autosave-label">
            <FontAwesomeIcon icon={faSyncAlt} /> Auto-save{" "}
            <span>{autoSave ? "(5s after changes)" : "(disabled)"}</span>
          </span>
        </div>
        <div className="button-group">
          <button
            onClick={() => handleSave(false)}
            className="btn btn-primary"
            disabled={restarting}
          >
            <FontAwesomeIcon icon={faSave} /> Save Settings
          </button>
          <button
            onClick={handleSaveAndRestart}
            className="btn btn-primary"
            disabled={restarting}
          >
            <FontAwesomeIcon icon={faSyncAlt} /> Save & Restart Bot
          </button>
          <button
            onClick={handleReset}
            className="btn btn-outline"
            disabled={restarting}
          >
            <FontAwesomeIcon icon={faUndo} /> Reset
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="btn btn-outline"
            disabled={restarting}
          >
            <FontAwesomeIcon icon={faTimes} /> Cancel
          </button>
        </div>
      </div>

      {/* Web UI Configuration */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faGlobe} /> Web UI Configuration
          </h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label className="toggle-label">
              <span>Enable Web UI</span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.WEB_ENABLED === "True"}
                  onChange={(e) =>
                    updateSetting("WEB_ENABLED", e.target.checked)
                  }
                />
                <span className="toggle-slider"></span>
              </label>
            </label>
            <small className="form-text">
              {comments.WEB_ENABLED || "Enable/disable web interface"}
            </small>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>Web Host</label>
              <input
                type="text"
                value={settings.WEB_HOST || ""}
                onChange={(e) => updateSetting("WEB_HOST", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                {comments.WEB_HOST || "Use 0.0.0.0 for all interfaces"}
              </small>
            </div>

            <div className="form-group">
              <label>Web Port</label>
              <input
                type="number"
                value={settings.WEB_PORT || ""}
                onChange={(e) => updateSetting("WEB_PORT", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                {comments.WEB_PORT || "Port for web interface"}
              </small>
            </div>

            <div className="form-group">
              <label>Secret Key</label>
              <input
                type="password"
                value={settings.WEB_SECRET_KEY || ""}
                onChange={(e) =>
                  updateSetting("WEB_SECRET_KEY", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                {comments.WEB_SECRET_KEY || "Session secret key"}
              </small>
            </div>

            <div className="form-group">
              <label className="toggle-label">
                <span>Debug Mode</span>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={settings.WEB_DEBUG === "True"}
                    onChange={(e) =>
                      updateSetting("WEB_DEBUG", e.target.checked)
                    }
                  />
                  <span className="toggle-slider"></span>
                </label>
              </label>
              <small className="form-text">
                {comments.WEB_DEBUG || "Set to False in production"}
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Web Authentication */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faLock} /> Web Authentication
          </h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label className="toggle-label">
              <span>Enable Authentication</span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.WEB_AUTH_ENABLED === "True"}
                  onChange={(e) =>
                    updateSetting("WEB_AUTH_ENABLED", e.target.checked)
                  }
                />
                <span className="toggle-slider"></span>
              </label>
            </label>
            <small className="form-text">
              {comments.WEB_AUTH_ENABLED ||
                "Enable/disable built-in authentication"}
            </small>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>Web Username</label>
              <input
                type="text"
                value={settings.WEB_USERNAME || ""}
                onChange={(e) => updateSetting("WEB_USERNAME", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                {comments.WEB_USERNAME || "Admin username"}
              </small>
            </div>

            <div className="form-group">
              <label>Web Password</label>
              <input
                type="password"
                value={settings.WEB_PASSWORD || ""}
                onChange={(e) => updateSetting("WEB_PASSWORD", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                {comments.WEB_PASSWORD || "Admin password"}
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Bot Configuration */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faRobot} /> Bot Configuration
          </h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label>Bot Token</label>
              <input
                type="password"
                value={settings.BOT_TOKEN || ""}
                onChange={(e) => updateSetting("BOT_TOKEN", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                Your Discord bot authentication token
              </small>
            </div>

            <div className="form-group">
              <label>Command Prefix</label>
              <input
                type="text"
                value={settings.COMMAND_PREFIX || ""}
                onChange={(e) =>
                  updateSetting("COMMAND_PREFIX", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                Prefix for bot commands (e.g., !)
              </small>
            </div>

            <div className="form-group">
              <label>Guild ID</label>
              <input
                type="text"
                value={settings.GUILD_ID || ""}
                onChange={(e) => updateSetting("GUILD_ID", e.target.value)}
                className="form-control"
              />
              <small className="form-text">Your Discord server ID</small>
            </div>

            <div className="form-group">
              <label>Guild Name</label>
              <input
                type="text"
                value={settings.GUILD_NAME || ""}
                onChange={(e) => updateSetting("GUILD_NAME", e.target.value)}
                className="form-control"
              />
              <small className="form-text">Your Discord server name</small>
            </div>

            <div className="form-group">
              <label>Admin User ID</label>
              <input
                type="text"
                value={settings.ADMIN_USER_ID || ""}
                onChange={(e) => updateSetting("ADMIN_USER_ID", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                Discord user ID for receiving admin notifications
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Channels Configuration */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faHashtag} /> Channel Configuration
          </h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label>Welcome Channel ID</label>
              <input
                type="text"
                value={settings.WELCOME_CHANNEL_ID || ""}
                onChange={(e) =>
                  updateSetting("WELCOME_CHANNEL_ID", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                Channel where new member welcome messages are sent
              </small>
            </div>

            <div className="form-group">
              <label>System Channel ID</label>
              <input
                type="text"
                value={settings.SYSTEM_CHANNEL_ID || ""}
                onChange={(e) =>
                  updateSetting("SYSTEM_CHANNEL_ID", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                Channel for system notifications and logs
              </small>
            </div>

            <div className="form-group">
              <label>Rules Channel ID</label>
              <input
                type="text"
                value={settings.RULES_CHANNEL_ID || ""}
                onChange={(e) =>
                  updateSetting("RULES_CHANNEL_ID", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                Channel containing your server rules
              </small>
            </div>

            <div className="form-group">
              <label>Ticket Category ID</label>
              <input
                type="text"
                value={settings.TICKET_CATEGORY_ID || ""}
                onChange={(e) =>
                  updateSetting("TICKET_CATEGORY_ID", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                Discord category ID where tickets will be created
              </small>
            </div>

            <div className="form-group">
              <label>Ko-fi Channel ID</label>
              <input
                type="text"
                value={settings.KOFI_CHANNEL_ID || ""}
                onChange={(e) =>
                  updateSetting("KOFI_CHANNEL_ID", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                Channel where Ko-fi donation notifications will be posted
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Roles Configuration */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faShieldAlt} /> Role Configuration
          </h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label>Verified Role</label>
              <input
                type="text"
                value={settings.VERIFIED_ROLE || ""}
                onChange={(e) => updateSetting("VERIFIED_ROLE", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                Role assigned after completing verification
              </small>
            </div>

            <div className="form-group">
              <label>Member Role</label>
              <input
                type="text"
                value={settings.MEMBER_ROLE || ""}
                onChange={(e) => updateSetting("MEMBER_ROLE", e.target.value)}
                className="form-control"
              />
              <small className="form-text">Role for general members</small>
            </div>

            <div className="form-group">
              <label>Staff Role</label>
              <input
                type="text"
                value={settings.STAFF_ROLE || ""}
                onChange={(e) => updateSetting("STAFF_ROLE", e.target.value)}
                className="form-control"
              />
              <small className="form-text">Role for staff members</small>
            </div>

            <div className="form-group">
              <label>Announcement Role</label>
              <input
                type="text"
                value={settings.ANNOUNCEMENT_ROLE || ""}
                onChange={(e) =>
                  updateSetting("ANNOUNCEMENT_ROLE", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">Role for announcement pings</small>
            </div>

            <div className="form-group">
              <label>Unverified Role</label>
              <input
                type="text"
                value={settings.UNVERIFIED_ROLE || ""}
                onChange={(e) =>
                  updateSetting("UNVERIFIED_ROLE", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                Role for new members before verification
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Plex Integration */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faFilm} /> Plex Integration
          </h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label className="toggle-label">
              <span>Enable Plex Integration</span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.PLEX_ENABLED === "True"}
                  onChange={(e) =>
                    updateSetting("PLEX_ENABLED", e.target.checked)
                  }
                />
                <span className="toggle-slider"></span>
              </label>
            </label>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>Plex Server Name</label>
              <input
                type="text"
                value={settings.PLEX_SERVER_NAME || ""}
                onChange={(e) =>
                  updateSetting("PLEX_SERVER_NAME", e.target.value)
                }
                className="form-control"
              />
              <small className="form-text">
                The name of your Plex Media Server
              </small>
            </div>

            <div className="form-group">
              <label>Plex Base URL</label>
              <input
                type="text"
                value={settings.PLEX_BASE_URL || ""}
                onChange={(e) => updateSetting("PLEX_BASE_URL", e.target.value)}
                className="form-control"
              />
              <small className="form-text">Your Plex server URL</small>
            </div>

            <div className="form-group">
              <label>Plex Token</label>
              <input
                type="password"
                value={settings.PLEX_TOKEN || ""}
                onChange={(e) => updateSetting("PLEX_TOKEN", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                Your Plex authentication token
              </small>
            </div>

            <div className="form-group">
              <label>Plex Username</label>
              <input
                type="text"
                value={settings.PLEX_USER || ""}
                onChange={(e) => updateSetting("PLEX_USER", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                Alternative to token authentication
              </small>
            </div>

            <div className="form-group">
              <label>Plex Password</label>
              <input
                type="password"
                value={settings.PLEX_PASS || ""}
                onChange={(e) => updateSetting("PLEX_PASS", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                Alternative to token authentication
              </small>
            </div>

            <div className="form-group">
              <label>Plex Roles</label>
              <input
                type="text"
                value={settings.PLEX_ROLES || ""}
                onChange={(e) => updateSetting("PLEX_ROLES", e.target.value)}
                className="form-control"
              />
              <small className="form-text">
                Comma-separated Discord role names that trigger Plex invites
              </small>
            </div>

            <div className="form-group full-width">
              <label>Plex Libraries</label>
              <textarea
                value={settings.PLEX_LIBS || ""}
                onChange={(e) => updateSetting("PLEX_LIBS", e.target.value)}
                className="form-control"
                rows={3}
              />
              <small className="form-text">
                Comma-separated library names to share, or "all"
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Logging Configuration */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faFileAlt} /> Logging Configuration
          </h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label>Logging Level</label>
              <select
                value={settings.LOGGING_LEVEL || "INFO"}
                onChange={(e) => updateSetting("LOGGING_LEVEL", e.target.value)}
                className="form-control"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
              <small className="form-text">Log verbosity level</small>
            </div>

            <div className="form-group">
              <label>Log File Path</label>
              <input
                type="text"
                value={settings.LOG_FILE || ""}
                onChange={(e) => updateSetting("LOG_FILE", e.target.value)}
                className="form-control"
              />
              <small className="form-text">Path where bot logs are saved</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
