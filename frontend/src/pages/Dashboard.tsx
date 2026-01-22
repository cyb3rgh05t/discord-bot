import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTachometerAlt,
  faClock,
  faSignal,
  faServer,
  faUsers,
  faHashtag,
  faShieldAlt,
  faTerminal,
  faCheckCircle,
  faTicketAlt,
  faCheck,
  faList,
  faUserPlus,
  faTimesCircle,
  faDatabase,
  faTable,
  faListOl,
  faMicrochip,
  faMemory,
  faHdd,
  faTasks,
  faBolt,
  faChartBar,
  faCog,
  faArrowRight,
  faFilm,
  faCoffee,
  faRobot,
  faGlobe,
} from "@fortawesome/free-solid-svg-icons";

interface BotStatus {
  online: boolean;
  name: string;
  latency: string;
  uptime: string;
  guilds: number;
  users: number;
}

interface BotStats {
  channels: number;
  roles: number;
  commands: number;
}

interface TicketStats {
  open: number;
  closed: number;
  total: number;
}

interface InviteStats {
  active: number;
  expired: number;
  total: number;
}

interface DatabaseStats {
  databases: number;
  tables: number;
  records: number;
}

interface ResourceItem {
  percent: number;
  label: string;
}

interface SystemResources {
  cpu: ResourceItem;
  memory: ResourceItem;
  disk: ResourceItem;
}

interface ServiceItem {
  name: string;
  status: string;
  icon: string;
}

interface DashboardData {
  bot_status: BotStatus;
  bot_stats: BotStats;
  ticket_stats: TicketStats;
  invite_stats: InviteStats;
  db_stats: DatabaseStats;
  resources: SystemResources;
  services: ServiceItem[];
  services_running: number;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get<DashboardData>("/dashboard/");
      setData(response.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  const getResourceClass = (percent: number) => {
    if (percent > 80) return "danger";
    if (percent > 60) return "warning";
    return "success";
  };

  const getServiceIcon = (icon: string) => {
    const iconMap: { [key: string]: any } = {
      "fa-robot": faRobot,
      "fa-globe": faGlobe,
      "fa-film": faFilm,
      "fa-coffee": faCoffee,
    };
    return iconMap[icon] || faServer;
  };

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faTachometerAlt} /> Dashboard
        </h1>
        <p className="subtitle">Comprehensive overview of your Discord bot</p>
      </div>

      {/* Bot Status Overview */}
      <div className="status-banner">
        <div className="status-main">
          <div className="status-indicator-wrapper">
            <div className="status-indicator">
              <span
                className={`status-dot ${
                  data.bot_status.online ? "online" : "offline"
                }`}
              ></span>
              <h2
                className={
                  data.bot_status.online ? "status-online" : "status-offline"
                }
              >
                {data.bot_status.name}
              </h2>
            </div>
          </div>
          <div className="status-details">
            <div className="status-item">
              <FontAwesomeIcon icon={faClock} />
              <span className="label">Uptime</span>
              <span className="value">{data.bot_status.uptime}</span>
            </div>
            <div className="status-item">
              <FontAwesomeIcon icon={faSignal} />
              <span className="label">Latency</span>
              <span className="value">{data.bot_status.latency}ms</span>
            </div>
            <div className="status-item">
              <FontAwesomeIcon icon={faServer} />
              <span className="label">Guilds</span>
              <span className="value">{data.bot_status.guilds}</span>
            </div>
            <div className="status-item">
              <FontAwesomeIcon icon={faUsers} />
              <span className="label">Members</span>
              <span className="value">{data.bot_status.users}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-icon channels-icon">
            <FontAwesomeIcon icon={faHashtag} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.bot_stats.channels}</div>
            <div className="stat-label">Channels</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon roles-icon">
            <FontAwesomeIcon icon={faShieldAlt} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.bot_stats.roles}</div>
            <div className="stat-label">Roles</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon commands-icon">
            <FontAwesomeIcon icon={faTerminal} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.bot_stats.commands}</div>
            <div className="stat-label">Commands</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon services-icon">
            <FontAwesomeIcon icon={faCheckCircle} />
          </div>
          <div className="stat-info">
            <div className="stat-value">
              {data.services_running}/{data.services.length}
            </div>
            <div className="stat-label">Services Running</div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-grid">
        {/* Tickets Overview */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faTicketAlt} /> Support Tickets
            </h3>
            <button
              onClick={() => navigate("/tickets")}
              className="btn btn-sm btn-outline"
            >
              View All <FontAwesomeIcon icon={faArrowRight} />
            </button>
          </div>
          <div className="card-body">
            <div className="mini-stats">
              <div className="mini-stat">
                <div className="mini-stat-icon open-icon">
                  <FontAwesomeIcon icon={faTicketAlt} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.ticket_stats.open}
                  </div>
                  <div className="mini-stat-label">Open</div>
                </div>
              </div>
              <div className="mini-stat">
                <div className="mini-stat-icon closed-icon">
                  <FontAwesomeIcon icon={faCheck} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.ticket_stats.closed}
                  </div>
                  <div className="mini-stat-label">Closed</div>
                </div>
              </div>
              <div className="mini-stat">
                <div className="mini-stat-icon total-icon">
                  <FontAwesomeIcon icon={faList} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.ticket_stats.total}
                  </div>
                  <div className="mini-stat-label">Total</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Invites Overview */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faUserPlus} /> Plex Invites
            </h3>
            <button
              onClick={() => navigate("/invites")}
              className="btn btn-sm btn-outline"
            >
              View All <FontAwesomeIcon icon={faArrowRight} />
            </button>
          </div>
          <div className="card-body">
            <div className="mini-stats">
              <div className="mini-stat">
                <div className="mini-stat-icon active-icon">
                  <FontAwesomeIcon icon={faCheckCircle} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.invite_stats.active}
                  </div>
                  <div className="mini-stat-label">Active</div>
                </div>
              </div>
              <div className="mini-stat">
                <div className="mini-stat-icon expired-icon">
                  <FontAwesomeIcon icon={faTimesCircle} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.invite_stats.expired}
                  </div>
                  <div className="mini-stat-label">Expired</div>
                </div>
              </div>
              <div className="mini-stat">
                <div className="mini-stat-icon total-icon">
                  <FontAwesomeIcon icon={faUsers} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.invite_stats.total}
                  </div>
                  <div className="mini-stat-label">Total</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Database Overview */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faDatabase} /> Databases
            </h3>
            <button
              onClick={() => navigate("/databases")}
              className="btn btn-sm btn-outline"
            >
              Browse <FontAwesomeIcon icon={faArrowRight} />
            </button>
          </div>
          <div className="card-body">
            <div className="mini-stats">
              <div className="mini-stat">
                <div className="mini-stat-icon db-icon">
                  <FontAwesomeIcon icon={faDatabase} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.db_stats.databases}
                  </div>
                  <div className="mini-stat-label">Databases</div>
                </div>
              </div>
              <div className="mini-stat">
                <div className="mini-stat-icon table-icon">
                  <FontAwesomeIcon icon={faTable} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">{data.db_stats.tables}</div>
                  <div className="mini-stat-label">Tables</div>
                </div>
              </div>
              <div className="mini-stat">
                <div className="mini-stat-icon records-icon">
                  <FontAwesomeIcon icon={faListOl} />
                </div>
                <div className="mini-stat-content">
                  <div className="mini-stat-value">
                    {data.db_stats.records.toLocaleString()}
                  </div>
                  <div className="mini-stat-label">Records</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Resources */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faMicrochip} /> System Resources
            </h3>
            <button
              onClick={() => navigate("/services")}
              className="btn btn-sm btn-outline"
            >
              Details <FontAwesomeIcon icon={faArrowRight} />
            </button>
          </div>
          <div className="card-body">
            <div className="resource-bars">
              <div className="resource-item">
                <div className="resource-header">
                  <span className="resource-label">
                    <FontAwesomeIcon icon={faMicrochip} /> CPU
                  </span>
                  <span className="resource-value">
                    {data.resources.cpu.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className={`progress-fill ${getResourceClass(
                      data.resources.cpu.percent
                    )}`}
                    style={{ width: `${data.resources.cpu.percent}%` }}
                  ></div>
                </div>
              </div>
              <div className="resource-item">
                <div className="resource-header">
                  <span className="resource-label">
                    <FontAwesomeIcon icon={faMemory} /> Memory
                  </span>
                  <span className="resource-value">
                    {data.resources.memory.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className={`progress-fill ${getResourceClass(
                      data.resources.memory.percent
                    )}`}
                    style={{ width: `${data.resources.memory.percent}%` }}
                  ></div>
                </div>
              </div>
              <div className="resource-item">
                <div className="resource-header">
                  <span className="resource-label">
                    <FontAwesomeIcon icon={faHdd} /> Disk
                  </span>
                  <span className="resource-value">
                    {data.resources.disk.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className={`progress-fill ${getResourceClass(
                      data.resources.disk.percent
                    )}`}
                    style={{ width: `${data.resources.disk.percent}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Services Status */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faTasks} /> Services
            </h3>
            <button
              onClick={() => navigate("/services")}
              className="btn btn-sm btn-outline"
            >
              Monitor <FontAwesomeIcon icon={faArrowRight} />
            </button>
          </div>
          <div className="card-body">
            <div className="services-list">
              {data.services.map((service, index) => (
                <div key={index} className="service-item">
                  <div className="service-name">
                    <FontAwesomeIcon icon={getServiceIcon(service.icon)} />
                    {service.name}
                  </div>
                  <div className={`service-status ${service.status}`}>
                    <span className="status-dot"></span>
                    {service.status.charAt(0).toUpperCase() +
                      service.status.slice(1)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faBolt} /> Quick Actions
            </h3>
          </div>
          <div className="card-body">
            <div className="action-grid">
              <button
                onClick={() => navigate("/members")}
                className="action-btn"
              >
                <FontAwesomeIcon icon={faUsers} />
                <span>Members</span>
              </button>
              <button
                onClick={() => navigate("/commands")}
                className="action-btn"
              >
                <FontAwesomeIcon icon={faTerminal} />
                <span>Commands</span>
              </button>
              <button
                onClick={() => navigate("/guild-stats")}
                className="action-btn"
              >
                <FontAwesomeIcon icon={faChartBar} />
                <span>Guild Stats</span>
              </button>
              <button
                onClick={() => navigate("/settings")}
                className="action-btn"
              >
                <FontAwesomeIcon icon={faCog} />
                <span>Settings</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
