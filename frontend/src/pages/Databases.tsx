import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faDatabase,
  faTable,
  faListOl,
  faChevronDown,
  faEye,
  faTerminal,
  faCode,
  faPlay,
  faInfoCircle,
  faLock,
  faSpinner,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";

interface TableInfo {
  database: string;
  name: string;
}

interface DatabaseStats {
  databases: number;
  tables: number;
  records: number;
}

interface DatabasesResponse {
  tables: TableInfo[];
  stats: DatabaseStats;
}

interface QueryResponse {
  success: boolean;
  results?: any[][];
  message?: string;
}

export default function Databases() {
  const navigate = useNavigate();
  const [data, setData] = useState<DatabasesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedDbs, setExpandedDbs] = useState<Set<string>>(new Set());
  const [query, setQuery] = useState("");
  const [queryResults, setQueryResults] = useState<QueryResponse | null>(null);
  const [queryLoading, setQueryLoading] = useState(false);

  useEffect(() => {
    const fetchDatabases = async () => {
      try {
        const response = await api.get<DatabasesResponse>("/databases/");
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch databases:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDatabases();
  }, []);

  const toggleDatabase = (dbName: string) => {
    const newExpanded = new Set(expandedDbs);
    if (newExpanded.has(dbName)) {
      newExpanded.delete(dbName);
    } else {
      newExpanded.add(dbName);
    }
    setExpandedDbs(newExpanded);
  };

  const executeQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    setQueryLoading(true);

    try {
      const response = await api.post<QueryResponse>("/databases/query", {
        query,
      });
      setQueryResults(response.data);
    } catch (error) {
      console.error("Query execution failed:", error);
      setQueryResults({
        success: false,
        message: "Failed to execute query",
      });
    } finally {
      setQueryLoading(false);
    }
  };

  // Group tables by database
  const groupedDatabases: Record<string, string[]> = {};
  if (data) {
    data.tables.forEach((table) => {
      if (!groupedDatabases[table.database]) {
        groupedDatabases[table.database] = [];
      }
      groupedDatabases[table.database].push(table.name);
    });
  }

  if (loading) {
    return <LoadingSpinner message="Loading databases..." />;
  }

  return (
    <div className="databases-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faDatabase} /> Database Browser
        </h1>
        <p className="subtitle">Explore your bot databases and tables</p>
      </div>

      {/* Statistics Cards */}
      {data && (
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-icon total-databases">
              <FontAwesomeIcon icon={faDatabase} />
            </div>
            <div className="stat-info">
              <div className="stat-value">{data.stats.databases}</div>
              <div className="stat-label">Databases</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon total-tables">
              <FontAwesomeIcon icon={faTable} />
            </div>
            <div className="stat-info">
              <div className="stat-value">{data.stats.tables}</div>
              <div className="stat-label">Tables</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon total-records">
              <FontAwesomeIcon icon={faListOl} />
            </div>
            <div className="stat-info">
              <div className="stat-value">
                {data.stats.records.toLocaleString()}
              </div>
              <div className="stat-label">Total Records</div>
            </div>
          </div>
        </div>
      )}

      {/* Databases Grid */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faDatabase} /> Available Databases
          </h3>
        </div>
        <div className="card-body">
          {Object.keys(groupedDatabases).length === 0 ? (
            <div className="empty-state">
              <FontAwesomeIcon icon={faDatabase} />
              <h3>No databases found</h3>
              <p>No database files were found in the databases directory.</p>
            </div>
          ) : (
            <div className="databases-grid">
              {Object.entries(groupedDatabases).map(([dbName, tables]) => (
                <div key={dbName} className="database-card">
                  <div
                    className="database-header"
                    onClick={() => toggleDatabase(dbName)}
                  >
                    <div className="database-info">
                      <FontAwesomeIcon icon={faDatabase} />
                      <h4>{dbName}.db</h4>
                      <span className="table-count">
                        {tables.length} table{tables.length !== 1 ? "s" : ""}
                      </span>
                    </div>
                    <FontAwesomeIcon
                      icon={faChevronDown}
                      className="expand-icon"
                      style={{
                        transform: expandedDbs.has(dbName)
                          ? "rotate(180deg)"
                          : "rotate(0deg)",
                      }}
                    />
                  </div>
                  {expandedDbs.has(dbName) && (
                    <div className="database-content">
                      <div className="tables-list">
                        {tables.map((table) => (
                          <div key={table} className="table-item">
                            <div
                              className="table-card-clickable"
                              onClick={() =>
                                navigate(`/databases/table/${table}`)
                              }
                            >
                              <div className="table-info">
                                <FontAwesomeIcon icon={faTable} />
                                <span>{table}</span>
                              </div>
                              <FontAwesomeIcon
                                icon={faEye}
                                className="view-icon"
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Query Console */}
      <div className="card">
        <div className="card-header">
          <div className="header-content">
            <h3>
              <FontAwesomeIcon icon={faTerminal} /> Query Console
            </h3>
            <span className="badge badge-warning">
              <FontAwesomeIcon icon={faLock} /> Read-only
            </span>
          </div>
        </div>
        <div className="card-body">
          <form onSubmit={executeQuery}>
            <div className="form-group">
              <label htmlFor="sqlQuery">
                <FontAwesomeIcon icon={faCode} /> SQL Query
              </label>
              <textarea
                id="sqlQuery"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="code-input"
                rows={4}
                placeholder="SELECT * FROM table_name LIMIT 10;"
              />
              <small className="form-text">
                <FontAwesomeIcon icon={faInfoCircle} /> Only SELECT queries are
                allowed for safety
              </small>
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={queryLoading}
            >
              <FontAwesomeIcon
                icon={queryLoading ? faSpinner : faPlay}
                spin={queryLoading}
              />{" "}
              Execute Query
            </button>
          </form>

          {queryResults && (
            <div className="query-results">
              <h4>
                <FontAwesomeIcon icon={faTable} /> Results:
              </h4>
              {queryResults.success ? (
                queryResults.results && queryResults.results.length > 0 ? (
                  <div className="table-responsive">
                    <table className="data-table">
                      <tbody>
                        {queryResults.results.map((row, i) => (
                          <tr key={i}>
                            {row.map((cell, j) => (
                              <td key={j}>
                                {cell !== null ? (
                                  cell
                                ) : (
                                  <span className="null-value">NULL</span>
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="no-results">
                    <FontAwesomeIcon icon={faInfoCircle} /> No results found.
                  </p>
                )
              ) : (
                <div className="error-message">
                  <FontAwesomeIcon icon={faExclamationCircle} />
                  <strong>Error:</strong> {queryResults.message}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
