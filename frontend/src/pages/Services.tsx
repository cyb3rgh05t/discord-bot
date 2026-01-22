import { useEffect, useState } from "react";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faServer,
  faRobot,
  faDatabase,
  faFilm,
  faCoffee,
  faClock,
  faMicrochip,
  faMemory,
  faHardDrive,
  faSync,
} from "@fortawesome/free-solid-svg-icons";

interface Service {
  name: string;
  status: "running" | "stopped" | "disabled";
  icon: string;
  uptime: string;
}

interface SystemResources {
  cpu: {
    percent: number;
    cores: number;
  };
  memory: {
    percent: number;
    used: number;
    total: number;
  };
  disk: {
    percent: number;
    used: number;
    total: number;
  };
}

const serviceIcons: Record<string, any> = {
  "Discord Bot": faRobot,
  Database: faDatabase,
  "Plex Integration": faFilm,
  "Ko-fi Webhook": faCoffee,
};

export default function Services() {
  const [services, setServices] = useState<Service[]>([]);
  const [resources, setResources] = useState<SystemResources | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchServicesData();
    const interval = setInterval(fetchServicesData, 60000); // Auto-refresh every 60s
    return () => clearInterval(interval);
  }, []);

  const fetchServicesData = async () => {
    try {
      const response = await api.get("/services/");
      if (response.data) {
        setServices(response.data.services || []);
        setResources(response.data.resources || null);
      }
    } catch (error) {
      console.error("Failed to fetch services data:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchServicesData();
  };

  const getProgressBarColor = (percent: number) => {
    if (percent > 90) return "progress-fill-danger";
    if (percent > 70) return "progress-fill-warning";
    return "progress-fill-success";
  };

  if (loading) {
    return <LoadingSpinner message="Loading services..." />;
  }

  return (
    <div className="services-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faServer} /> Service Monitor
        </h1>
        <p className="subtitle">Monitor system resources and service health</p>
      </div>

      {/* Services Status */}
      <div className="card mb-6">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faServer} className="w-5 h-5 inline" />{" "}
            Services
          </h3>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn btn-sm btn-outline"
          >
            <FontAwesomeIcon
              icon={faSync}
              className={`w-4 h-4 inline ${refreshing ? "animate-spin" : ""}`}
            />{" "}
            Refresh
          </button>
        </div>
        <div className="card-body">
          <div className="services-grid">
            {services.map((service, index) => {
              const icon = serviceIcons[service.name] || faServer;

              return (
                <div key={index} className="service-card">
                  <div className="service-icon">
                    <FontAwesomeIcon icon={icon} className="w-6 h-6" />
                  </div>
                  <div className="service-info">
                    <h4>{service.name}</h4>
                    <div className={`service-status ${service.status}`}>
                      <span className="status-dot"></span>
                      <span>
                        {service.status.charAt(0).toUpperCase() +
                          service.status.slice(1)}
                      </span>
                    </div>
                    {service.uptime !== "N/A" && (
                      <p className="service-uptime">
                        <FontAwesomeIcon
                          icon={faClock}
                          className="w-4 h-4 inline"
                        />{" "}
                        {service.uptime}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* System Resources */}
      {resources && (
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faMicrochip} className="w-5 h-5 inline" />{" "}
              System Resources
            </h3>
          </div>
          <div className="card-body">
            <div className="resource-grid">
              {/* CPU */}
              <div className="resource-item">
                <div className="resource-icon">
                  <FontAwesomeIcon icon={faMicrochip} className="w-6 h-6" />
                </div>
                <div className="resource-info">
                  <h4>CPU Usage</h4>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${getProgressBarColor(
                        resources.cpu.percent
                      )}`}
                      style={{ width: `${resources.cpu.percent}%` }}
                    ></div>
                  </div>
                  <p className="resource-stats">
                    <span className="stat-value">
                      {resources.cpu.percent.toFixed(1)}%
                    </span>
                    <span className="stat-label">
                      {resources.cpu.cores} cores
                    </span>
                  </p>
                </div>
              </div>

              {/* Memory */}
              <div className="resource-item">
                <div className="resource-icon">
                  <FontAwesomeIcon icon={faMemory} className="w-6 h-6" />
                </div>
                <div className="resource-info">
                  <h4>Memory Usage</h4>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${getProgressBarColor(
                        resources.memory.percent
                      )}`}
                      style={{ width: `${resources.memory.percent}%` }}
                    ></div>
                  </div>
                  <p className="resource-stats">
                    <span className="stat-value">
                      {resources.memory.percent.toFixed(1)}%
                    </span>
                    <span className="stat-label">
                      {resources.memory.used.toFixed(2)} /{" "}
                      {resources.memory.total.toFixed(2)} GB
                    </span>
                  </p>
                </div>
              </div>

              {/* Disk */}
              <div className="resource-item">
                <div className="resource-icon">
                  <FontAwesomeIcon icon={faHardDrive} className="w-6 h-6" />
                </div>
                <div className="resource-info">
                  <h4>Disk Usage</h4>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${getProgressBarColor(
                        resources.disk.percent
                      )}`}
                      style={{ width: `${resources.disk.percent}%` }}
                    ></div>
                  </div>
                  <p className="resource-stats">
                    <span className="stat-value">
                      {resources.disk.percent.toFixed(1)}%
                    </span>
                    <span className="stat-label">
                      {resources.disk.used.toFixed(2)} /{" "}
                      {resources.disk.total.toFixed(2)} GB
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
