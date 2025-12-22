import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTicket,
  faCheck,
  faList,
  faUser,
  faEye,
  faTimes,
  faSearch,
  faSync,
  faChevronLeft,
  faChevronRight,
  faFilm,
  faTv,
} from "@fortawesome/free-solid-svg-icons";

interface TicketItem {
  id: number;
  user_id: string;
  username: string;
  type: string;
  ticket_type?: string;
  status: string;
  created_at: string;
}

interface TicketStats {
  total: number;
  open: number;
  closed: number;
}

export default function Tickets() {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState<TicketItem[]>([]);
  const [stats, setStats] = useState<TicketStats>({
    total: 0,
    open: 0,
    closed: 0,
  });
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (loading) {
      fetchTickets();
    } else {
      fetchTickets(false);
    }
  }, [statusFilter, typeFilter, currentPage, searchQuery]);

  const fetchTickets = async (showLoader = false) => {
    try {
      if (showLoader) {
        setLoading(true);
      }
      const params = new URLSearchParams({
        status: statusFilter,
        type: typeFilter,
        page: currentPage.toString(),
      });
      if (searchQuery) {
        params.append("search", searchQuery);
      }

      const response = await api.get(`/tickets/?${params}`);
      if (response.data) {
        setTickets(response.data.tickets || []);
        setStats(response.data.stats || { total: 0, open: 0, closed: 0 });
        setTotalPages(response.data.total_pages || 1);
      }
    } catch (error) {
      console.error("Failed to fetch tickets:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchTickets(false);
  };

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setCurrentPage(1);
    }
  };

  const handleCloseTicket = async (ticketId: number) => {
    if (!confirm("Are you sure you want to close this ticket?")) {
      return;
    }

    try {
      await api.post(`/tickets/${ticketId}/close`);
      fetchTickets();
    } catch (error) {
      console.error("Failed to close ticket:", error);
      alert("Failed to close ticket");
    }
  };

  const getPageNumbers = () => {
    const pages = [];
    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 ||
        i === totalPages ||
        (i >= currentPage - 2 && i <= currentPage + 2)
      ) {
        pages.push(i);
      } else if (i === currentPage - 3 || i === currentPage + 3) {
        pages.push("...");
      }
    }
    return pages;
  };

  if (loading) {
    return <LoadingSpinner message="Loading tickets..." />;
  }

  return (
    <div className="tickets-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faTicket} /> Support Tickets
        </h1>
        <p className="subtitle">View and manage support tickets</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon open-tickets">
            <FontAwesomeIcon icon={faTicket} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.open}</div>
            <div className="stat-label">Open Tickets</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon closed-tickets">
            <FontAwesomeIcon icon={faCheck} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.closed}</div>
            <div className="stat-label">Closed Tickets</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon total-tickets">
            <FontAwesomeIcon icon={faList} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Tickets</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>Filter by Status:</label>
          <div className="btn-group">
            <button
              onClick={() => {
                setStatusFilter("all");
                setCurrentPage(1);
              }}
              className={`btn btn-sm ${
                statusFilter === "all" ? "btn-primary" : "btn-outline"
              }`}
            >
              All
            </button>
            <button
              onClick={() => {
                setStatusFilter("open");
                setCurrentPage(1);
              }}
              className={`btn btn-sm ${
                statusFilter === "open" ? "btn-primary" : "btn-outline"
              }`}
            >
              Open
            </button>
            <button
              onClick={() => {
                setStatusFilter("closed");
                setCurrentPage(1);
              }}
              className={`btn btn-sm ${
                statusFilter === "closed" ? "btn-primary" : "btn-outline"
              }`}
            >
              Closed
            </button>
          </div>
        </div>

        <div className="filter-group">
          <label>Filter by Type:</label>
          <div className="btn-group">
            <button
              onClick={() => {
                setTypeFilter("all");
                setCurrentPage(1);
              }}
              className={`btn btn-sm ${
                typeFilter === "all" ? "btn-primary" : "btn-outline"
              }`}
            >
              All
            </button>
            <button
              onClick={() => {
                setTypeFilter("plex");
                setCurrentPage(1);
              }}
              className={`btn btn-sm ${
                typeFilter === "plex" ? "btn-primary" : "btn-outline"
              }`}
            >
              <FontAwesomeIcon icon={faFilm} className="w-4 h-4" /> Plex
            </button>
            <button
              onClick={() => {
                setTypeFilter("tv");
                setCurrentPage(1);
              }}
              className={`btn btn-sm ${
                typeFilter === "tv" ? "btn-primary" : "btn-outline"
              }`}
            >
              <FontAwesomeIcon icon={faTv} className="w-4 h-4" /> TV
            </button>
          </div>
        </div>
      </div>

      {/* Tickets Table */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faList} className="w-5 h-5 inline" /> Tickets
          </h3>
          <div className="flex gap-3 items-center">
            <div className="search-box">
              <FontAwesomeIcon
                icon={faSearch}
                className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted"
              />
              <input
                type="text"
                placeholder="Search tickets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleSearch}
                className="form-input"
              />
            </div>
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
        </div>

        <div className="card-body">
          {tickets.length > 0 ? (
            <div className="table-responsive">
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((ticket) => (
                    <tr key={ticket.id}>
                      <td>#{ticket.id}</td>
                      <td>
                        <span className="user-icon">
                          <FontAwesomeIcon icon={faUser} className="w-4 h-4" />
                        </span>
                        {ticket.username}
                      </td>
                      <td>{ticket.type || "N/A"}</td>
                      <td>
                        <span
                          className={`badge ${
                            ticket.status === "open"
                              ? "badge-success"
                              : "badge-secondary"
                          }`}
                        >
                          {ticket.status.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        {ticket.created_at
                          ? ticket.created_at.substring(0, 16)
                          : "N/A"}
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => navigate(`/tickets/${ticket.id}`)}
                            className="btn btn-sm btn-primary"
                            title="View"
                          >
                            <FontAwesomeIcon icon={faEye} className="w-4 h-4" />
                          </button>
                          {ticket.status === "open" && (
                            <button
                              onClick={() => handleCloseTicket(ticket.id)}
                              className="btn btn-sm"
                              title="Close"
                            >
                              <FontAwesomeIcon
                                icon={faTimes}
                                className="w-4 h-4"
                              />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <FontAwesomeIcon
                icon={faTicket}
                className="w-16 h-16 mx-auto text-text-muted mb-4"
              />
              <h3>No tickets found</h3>
              <p>There are no tickets matching your filter criteria.</p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="card-footer">
            <div className="pagination-container">
              <div className="pagination-info">
                Showing {(currentPage - 1) * 10 + 1} -{" "}
                {Math.min(currentPage * 10, stats.total)} of {stats.total}{" "}
                tickets
              </div>
              <div className="pagination">
                {currentPage > 1 && (
                  <button
                    onClick={() => setCurrentPage(currentPage - 1)}
                    className="btn btn-sm"
                  >
                    <FontAwesomeIcon
                      icon={faChevronLeft}
                      className="w-4 h-4 inline"
                    />{" "}
                    Previous
                  </button>
                )}

                {getPageNumbers().map((page, index) =>
                  page === "..." ? (
                    <span key={index} className="btn btn-sm opacity-50">
                      ...
                    </span>
                  ) : (
                    <button
                      key={index}
                      onClick={() => setCurrentPage(page as number)}
                      className={`btn btn-sm ${
                        currentPage === page ? "btn-primary" : "btn-outline"
                      }`}
                    >
                      {page}
                    </button>
                  )
                )}

                {currentPage < totalPages && (
                  <button
                    onClick={() => setCurrentPage(currentPage + 1)}
                    className="btn btn-sm"
                  >
                    Next{" "}
                    <FontAwesomeIcon
                      icon={faChevronRight}
                      className="w-4 h-4 inline"
                    />
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
