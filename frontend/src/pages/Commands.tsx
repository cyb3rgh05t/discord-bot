import { useEffect, useState } from "react";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTerminal,
  faList,
  faSlash,
  faAt,
} from "@fortawesome/free-solid-svg-icons";

interface SlashCommand {
  name: string;
  description: string;
  type: string;
}

interface PrefixCommand {
  name: string;
  description: string;
  aliases: string[];
  type: string;
}

interface CommandStats {
  total: number;
  slash: number;
  prefix: number;
}

interface CommandsData {
  slash_commands: SlashCommand[];
  prefix_commands: PrefixCommand[];
  stats: CommandStats;
}

export default function Commands() {
  const [activeTab, setActiveTab] = useState<"slash" | "prefix">("slash");
  const [data, setData] = useState<CommandsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCommands();
  }, []);

  const fetchCommands = async () => {
    try {
      setLoading(true);
      const response = await api.get("/commands/");
      setData(response.data);
    } catch (error) {
      console.error("Error fetching commands:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading commands..." />;
  }

  return (
    <div className="commands-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faTerminal} />
          Bot Commands
        </h1>
        <p className="subtitle">View all available slash and prefix commands</p>
      </div>

      {/* Statistics */}
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-icon total-commands">
            <FontAwesomeIcon icon={faList} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data?.stats.total || 0}</div>
            <div className="stat-label">Total Commands</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon slash-commands">
            <FontAwesomeIcon icon={faSlash} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data?.stats.slash || 0}</div>
            <div className="stat-label">Slash Commands</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon prefix-commands">
            <FontAwesomeIcon icon={faAt} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data?.stats.prefix || 0}</div>
            <div className="stat-label">Prefix Commands</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab-button ${activeTab === "slash" ? "active" : ""}`}
          onClick={() => setActiveTab("slash")}
        >
          <FontAwesomeIcon icon={faSlash} /> Slash Commands
        </button>
        <button
          className={`tab-button ${activeTab === "prefix" ? "active" : ""}`}
          onClick={() => setActiveTab("prefix")}
        >
          <FontAwesomeIcon icon={faAt} /> Prefix Commands
        </button>
      </div>

      {/* Slash Commands Tab */}
      {activeTab === "slash" && (
        <div className="tab-content active">
          <div className="card">
            <div className="card-header">
              <h3>
                <FontAwesomeIcon icon={faSlash} /> Slash Commands (
                {data?.stats.slash || 0})
              </h3>
            </div>
            <div className="card-body">
              {data?.slash_commands && data.slash_commands.length > 0 ? (
                <div className="commands-grid">
                  {data.slash_commands.map((cmd, index) => (
                    <div key={index} className="command-card">
                      <div className="command-header">
                        <span className="command-name">
                          <FontAwesomeIcon icon={faSlash} /> {cmd.name}
                        </span>
                        <span className="command-type-badge slash">Slash</span>
                      </div>
                      <div className="command-description">
                        {cmd.description}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <FontAwesomeIcon icon={faSlash} />
                  <h3>No slash commands found</h3>
                  <p>The bot doesn't have any slash commands registered.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Prefix Commands Tab */}
      {activeTab === "prefix" && (
        <div className="tab-content active">
          <div className="card">
            <div className="card-header">
              <h3>
                <FontAwesomeIcon icon={faAt} /> Prefix Commands (
                {data?.stats.prefix || 0})
              </h3>
            </div>
            <div className="card-body">
              {data?.prefix_commands && data.prefix_commands.length > 0 ? (
                <div className="commands-grid">
                  {data.prefix_commands.map((cmd, index) => (
                    <div key={index} className="command-card">
                      <div className="command-header">
                        <span className="command-name">
                          <FontAwesomeIcon icon={faAt} /> {cmd.name}
                        </span>
                        <span className="command-type-badge prefix">
                          Prefix
                        </span>
                      </div>
                      <div className="command-description">
                        {cmd.description}
                      </div>
                      {cmd.aliases && cmd.aliases.length > 0 && (
                        <div className="command-aliases">
                          <strong>Aliases:</strong>
                          {cmd.aliases.map((alias, i) => (
                            <span key={i} className="alias-badge">
                              {alias}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <FontAwesomeIcon icon={faAt} />
                  <h3>No prefix commands found</h3>
                  <p>The bot doesn't have any prefix commands registered.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
