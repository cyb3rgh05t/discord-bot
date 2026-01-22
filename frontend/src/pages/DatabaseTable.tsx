import { useEffect, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTable,
  faArrowLeft,
  faChevronLeft,
  faChevronRight,
  faChevronDown,
  faColumns,
  faCheck,
  faTimes,
  faKey,
  faInbox,
} from "@fortawesome/free-solid-svg-icons";
import api from "@/lib/api";

interface ColumnSchema {
  cid: number;
  name: string;
  type: string;
  notnull: boolean;
  default: any;
  pk: boolean;
}

interface TableDataResponse {
  columns: string[];
  rows: any[][];
  table_schema: ColumnSchema[];
  page: number;
  per_page: number;
  total: number;
  database: string;
}

export default function DatabaseTable() {
  const { tableName } = useParams<{ tableName: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState<TableDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [schemaExpanded, setSchemaExpanded] = useState(false);

  const page = parseInt(searchParams.get("page") || "1", 10);

  useEffect(() => {
    const fetchTableData = async () => {
      try {
        const response = await api.get<TableDataResponse>(
          `/databases/table/${tableName}?page=${page}&per_page=50`
        );
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch table data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTableData();
  }, [tableName, page]);

  if (loading) {
    return <LoadingSpinner message="Loading table data..." />;
  }

  if (!data) {
    return (
      <div className="database-table-page">
        <div className="page-header">
          <div>
            <h1>
              <FontAwesomeIcon icon={faTable} /> {tableName}
            </h1>
            <p className="subtitle">Table not found</p>
          </div>
          <div className="header-actions">
            <button
              onClick={() => navigate("/databases")}
              className="btn-outline"
            >
              <FontAwesomeIcon icon={faArrowLeft} /> Back to Databases
            </button>
          </div>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / data.per_page);

  const goToPage = (newPage: number) => {
    setSearchParams({ page: newPage.toString() });
  };

  return (
    <div className="database-table-page">
      <div className="page-header">
        <div>
          <h1>
            <FontAwesomeIcon icon={faTable} /> {tableName}
          </h1>
          <p className="subtitle">
            Database: {data.database}.db | Total rows: {data.total}
          </p>
        </div>
        <div className="header-actions">
          <button
            onClick={() => navigate("/databases")}
            className="btn-outline"
          >
            <FontAwesomeIcon icon={faArrowLeft} /> Back to Databases
          </button>
        </div>
      </div>

      {/* Table Data */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faTable} /> Table Data
          </h3>
          <div className="pagination-info">
            Page {data.page} | {data.per_page} rows per page
          </div>
        </div>
        <div className="card-body">
          {data.rows.length > 0 ? (
            <>
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      {data.columns.map((column) => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.rows.map((row, i) => (
                      <tr key={i}>
                        {row.map((value, j) => (
                          <td key={j}>
                            {value !== null ? (
                              value
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

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination-container">
                  <div className="pagination">
                    {page > 1 && (
                      <button
                        onClick={() => goToPage(page - 1)}
                        className="page-link"
                      >
                        <FontAwesomeIcon icon={faChevronLeft} /> Previous
                      </button>
                    )}

                    <span className="page-info">
                      Page {page} of {totalPages}
                    </span>

                    {page < totalPages && (
                      <button
                        onClick={() => goToPage(page + 1)}
                        className="page-link"
                      >
                        Next <FontAwesomeIcon icon={faChevronRight} />
                      </button>
                    )}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <FontAwesomeIcon icon={faInbox} />
              <h3>No data</h3>
              <p>This table is empty.</p>
            </div>
          )}
        </div>
      </div>

      {/* Table Schema */}
      <div className="card">
        <div
          className="card-header clickable-header"
          onClick={() => setSchemaExpanded(!schemaExpanded)}
        >
          <h3>
            <FontAwesomeIcon icon={faColumns} /> Table Schema
          </h3>
          <FontAwesomeIcon
            icon={faChevronDown}
            className="expand-icon"
            style={{
              transform: schemaExpanded ? "rotate(180deg)" : "rotate(0deg)",
            }}
          />
        </div>
        {schemaExpanded && (
          <div className="card-body">
            <div className="schema-table">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Not Null</th>
                    <th>Default</th>
                    <th>Primary Key</th>
                  </tr>
                </thead>
                <tbody>
                  {data.table_schema.map((column) => (
                    <tr key={column.cid}>
                      <td>
                        <strong>{column.name}</strong>
                      </td>
                      <td>
                        <span className="type-badge">{column.type}</span>
                      </td>
                      <td>
                        {column.notnull ? (
                          <FontAwesomeIcon
                            icon={faCheck}
                            className="text-success"
                          />
                        ) : (
                          <FontAwesomeIcon
                            icon={faTimes}
                            className="text-muted"
                          />
                        )}
                      </td>
                      <td>{column.default !== null ? column.default : "-"}</td>
                      <td>
                        {column.pk ? (
                          <FontAwesomeIcon
                            icon={faKey}
                            className="text-warning"
                          />
                        ) : (
                          <FontAwesomeIcon
                            icon={faTimes}
                            className="text-muted"
                          />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
