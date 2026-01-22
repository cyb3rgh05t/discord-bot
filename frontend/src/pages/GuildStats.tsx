import { useEffect, useState } from "react";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faServer,
  faUsers,
  faHashtag,
  faShieldAlt,
  faCrown,
  faCircle,
  faInfoCircle,
  faCalendar,
} from "@fortawesome/free-solid-svg-icons";
import api from "@/lib/api";

interface GuildStat {
  id: string;
  name: string;
  icon: string | null;
  owner: string;
  owner_id: string;
  member_count: number;
  humans: number;
  bots: number;
  online: number;
  idle: number;
  dnd: number;
  offline: number;
  text_channels: number;
  voice_channels: number;
  categories: number;
  total_channels: number;
  role_count: number;
  emoji_count: number;
  created_at: string;
  boost_level: number;
  boost_count: number;
  verification_level: string;
}

interface GuildStatsResponse {
  guilds: GuildStat[];
  totals: {
    guilds: number;
    members: number;
    channels: number;
    roles: number;
  };
}

export default function GuildStats() {
  const [data, setData] = useState<GuildStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGuildStats = async () => {
      try {
        const response = await api.get<GuildStatsResponse>("/guild-stats/");
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch guild stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchGuildStats();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading guild statistics..." />;
  }

  if (!data) {
    return (
      <div className="guild-stats-page">
        <div className="page-header">
          <h1>
            <FontAwesomeIcon icon={faServer} /> Guild Statistics
          </h1>
          <p className="subtitle">View statistics for all connected guilds</p>
        </div>
        <div className="empty-state">
          <FontAwesomeIcon icon={faServer} />
          <h3>No guilds found</h3>
          <p>The bot is not connected to any guilds.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="guild-stats-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faServer} /> Guild Statistics
        </h1>
        <p className="subtitle">View statistics for all connected guilds</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-icon total-guilds">
            <FontAwesomeIcon icon={faServer} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.totals.guilds}</div>
            <div className="stat-label">Total Guilds</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon total-members">
            <FontAwesomeIcon icon={faUsers} />
          </div>
          <div className="stat-info">
            <div className="stat-value">
              {data.totals.members.toLocaleString()}
            </div>
            <div className="stat-label">Total Members</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon total-channels">
            <FontAwesomeIcon icon={faHashtag} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.totals.channels}</div>
            <div className="stat-label">Total Channels</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon total-roles">
            <FontAwesomeIcon icon={faShieldAlt} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.totals.roles}</div>
            <div className="stat-label">Total Roles</div>
          </div>
        </div>
      </div>

      {/* Guilds List */}
      <div className="guilds-list">
        {data.guilds.map((guild) => (
          <div key={guild.id} className="guild-card">
            {/* Guild Header */}
            <div className="guild-header">
              {guild.icon ? (
                <img src={guild.icon} alt={guild.name} className="guild-icon" />
              ) : (
                <div className="guild-icon-placeholder">
                  <FontAwesomeIcon icon={faServer} />
                </div>
              )}
              <div className="guild-info">
                <h3 className="guild-name">{guild.name}</h3>
                <div className="guild-owner">
                  <FontAwesomeIcon icon={faCrown} />
                  Owner: {guild.owner}
                </div>
              </div>
            </div>

            {/* Guild Body */}
            <div className="guild-body">
              <div className="stats-row">
                {/* Members Section */}
                <div className="stat-section">
                  <h5>
                    <FontAwesomeIcon icon={faUsers} /> Members
                  </h5>
                  <div className="stat-row">
                    <span className="stat-label">Total:</span>
                    <span className="stat-value">{guild.member_count}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Humans:</span>
                    <span className="stat-value">{guild.humans}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Bots:</span>
                    <span className="stat-value">{guild.bots}</span>
                  </div>
                </div>

                {/* Status Section */}
                <div className="stat-section">
                  <h5>
                    <FontAwesomeIcon icon={faCircle} /> Online Status
                  </h5>
                  <div className="stat-row">
                    <span className="stat-label">
                      <FontAwesomeIcon
                        icon={faCircle}
                        className="status-color-online"
                      />{" "}
                      Online:
                    </span>
                    <span className="stat-value">{guild.online}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">
                      <FontAwesomeIcon
                        icon={faCircle}
                        className="status-color-idle"
                      />{" "}
                      Idle:
                    </span>
                    <span className="stat-value">{guild.idle}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">
                      <FontAwesomeIcon
                        icon={faCircle}
                        className="status-color-dnd"
                      />{" "}
                      DND:
                    </span>
                    <span className="stat-value">{guild.dnd}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">
                      <FontAwesomeIcon
                        icon={faCircle}
                        className="status-color-offline"
                      />{" "}
                      Offline:
                    </span>
                    <span className="stat-value">{guild.offline}</span>
                  </div>
                </div>

                {/* Channels Section */}
                <div className="stat-section">
                  <h5>
                    <FontAwesomeIcon icon={faHashtag} /> Channels
                  </h5>
                  <div className="stat-row">
                    <span className="stat-label">Text:</span>
                    <span className="stat-value">{guild.text_channels}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Voice:</span>
                    <span className="stat-value">{guild.voice_channels}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Categories:</span>
                    <span className="stat-value">{guild.categories}</span>
                  </div>
                </div>

                {/* Other Stats */}
                <div className="stat-section">
                  <h5>
                    <FontAwesomeIcon icon={faInfoCircle} /> Other
                  </h5>
                  <div className="stat-row">
                    <span className="stat-label">Roles:</span>
                    <span className="stat-value">{guild.role_count}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Emojis:</span>
                    <span className="stat-value">{guild.emoji_count}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Boost Level:</span>
                    <span className="stat-value">{guild.boost_level}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Boosts:</span>
                    <span className="stat-value">{guild.boost_count}</span>
                  </div>
                </div>
              </div>

              {/* Guild Footer */}
              <div className="guild-footer">
                <div className="guild-meta">
                  <span className="meta-item">
                    <FontAwesomeIcon icon={faShieldAlt} />
                    {guild.verification_level}
                  </span>
                  <span className="meta-item">
                    <FontAwesomeIcon icon={faCalendar} />
                    {guild.created_at}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
