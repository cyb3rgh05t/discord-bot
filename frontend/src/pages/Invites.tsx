import { useEffect, useState } from "react";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUserPlus,
  faUsers,
  faCheckCircle,
  faTimesCircle,
  faUserTimes,
  faUserMinus,
  faServer,
  faFilm,
  faTv,
  faEnvelope,
  faTrash,
  faSearch,
  faSync,
  faChevronLeft,
  faChevronRight,
  faCodeBranch,
} from "@fortawesome/free-solid-svg-icons";

interface InviteItem {
  id: number;
  email: string;
  discord_user: string;
  status: string;
  created_at: string;
  expires_at?: string;
}

interface InviteStats {
  total: number;
  active: number;
  expired: number;
  revoked: number;
  removed: number;
}

interface PlexStats {
  connected: boolean;
  server_name: string;
  version: string;
  movies: number;
  shows: number;
  users: number;
}

export default function Invites() {
  const [invites, setInvites] = useState<InviteItem[]>([]);
  const [stats, setStats] = useState<InviteStats>({
    total: 0,
    active: 0,
    expired: 0,
    revoked: 0,
    removed: 0,
  });
  const [plexStats, setPlexStats] = useState<PlexStats>({
    connected: false,
    server_name: "N/A",
    version: "N/A",
    movies: 0,
    shows: 0,
    users: 0,
  });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [refreshing, setRefreshing] = useState(false);
  const [email, setEmail] = useState("");
  const [discordUser, setDiscordUser] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchInvites();
  }, [currentPage, searchQuery]);

  const fetchInvites = async () => {
    try {
      setLoading(true);
      const response = await api.get("/invites/", {
        params: {
          page: currentPage,
          per_page: 10,
          search: searchQuery || undefined,
        },
      });

      setInvites(response.data.invites);
      setStats(response.data.stats);
      setPlexStats(response.data.plex_stats);
      setTotalPages(response.data.total_pages);
    } catch (err) {
      console.error("Error fetching invites:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchInvites();
  };

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setCurrentPage(1);
      fetchInvites();
    }
  };

  const handleAddInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await api.post("/invites/add", {
        email,
        discord_user: discordUser,
      });

      if (response.data.success) {
        setEmail("");
        setDiscordUser("");
        fetchInvites();
      } else {
        alert("Error: " + response.data.message);
      }
    } catch (err: any) {
      alert(
        "Error adding invite: " + (err.response?.data?.message || err.message)
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemoveInvite = async (inviteId: number) => {
    if (!confirm("Are you sure you want to remove this invite?")) {
      return;
    }

    try {
      const response = await api.post(`/invites/${inviteId}/remove`);
      if (response.data.success) {
        fetchInvites();
      } else {
        alert("Error: " + response.data.message);
      }
    } catch (err: any) {
      alert(
        "Error removing invite: " + (err.response?.data?.message || err.message)
      );
    }
  };

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 4) {
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push("...");
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(1);
        pages.push("...");
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push("...");
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push("...");
        pages.push(totalPages);
      }
    }
    return pages;
  };

  if (loading) {
    return <LoadingSpinner message="Loading invites..." />;
  }

  return (
    <div className="invites-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faUserPlus} /> Plex Invites
        </h1>
        <p className="subtitle">Manage Plex user invitations</p>
      </div>

      {/* Statistics */}
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-icon total-invites">
            <FontAwesomeIcon icon={faUsers} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Invites</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon active-invites">
            <FontAwesomeIcon icon={faCheckCircle} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.active}</div>
            <div className="stat-label">Active</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon expired-invites">
            <FontAwesomeIcon icon={faTimesCircle} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.expired}</div>
            <div className="stat-label">Expired</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon revoked-invites">
            <FontAwesomeIcon icon={faUserTimes} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.revoked}</div>
            <div className="stat-label">Revoked</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon removed-invites">
            <FontAwesomeIcon icon={faUserMinus} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.removed}</div>
            <div className="stat-label">Removed</div>
          </div>
        </div>

        <div className="stat-card">
          <div
            className={`stat-icon ${
              plexStats.connected ? "success" : "warning"
            }`}
          >
            <FontAwesomeIcon icon={faServer} />
          </div>
          <div className="stat-info">
            <div className="stat-value">
              {plexStats.connected ? plexStats.users : "N/A"}
            </div>
            <div className="stat-label">Plex Users</div>
          </div>
        </div>
      </div>

      {/* Plex Server Status */}
      {plexStats.connected && (
        <div className="card plex-stats">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faServer} />
              Plex Server Status
            </h3>
            <span className="server-name">{plexStats.server_name}</span>
          </div>
          <div className="card-body">
            <div className="stats-grid stats-grid-4">
              <div className="stat-card">
                <div className="stat-icon plex-movies">
                  <FontAwesomeIcon icon={faFilm} />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{plexStats.movies}</div>
                  <div className="stat-label">Movies</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon plex-shows">
                  <FontAwesomeIcon icon={faTv} />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{plexStats.shows}</div>
                  <div className="stat-label">TV Shows</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon plex-users">
                  <FontAwesomeIcon icon={faUsers} />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{plexStats.users}</div>
                  <div className="stat-label">Users</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon plex-version">
                  <FontAwesomeIcon icon={faCodeBranch} />
                </div>
                <div className="stat-content">
                  <div className="stat-value stat-value-small">
                    {plexStats.version}
                  </div>
                  <div className="stat-label">Version</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Invite Form */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faUserPlus} />
            Add New Invite
          </h3>
        </div>
        <div className="card-body">
          <form onSubmit={handleAddInvite} className="invite-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">
                  <FontAwesomeIcon icon={faEnvelope} />
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="form-control"
                  placeholder="user@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="discord_user">
                  <FontAwesomeIcon icon={faUsers} />
                  Discord Username
                </label>
                <input
                  type="text"
                  id="discord_user"
                  name="discord_user"
                  className="form-control"
                  placeholder="Username#1234"
                  value={discordUser}
                  onChange={(e) => setDiscordUser(e.target.value)}
                  required
                />
              </div>
              <div className="form-group form-actions">
                <label>&nbsp;</label>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  <FontAwesomeIcon icon={faUserPlus} />
                  {submitting ? "Adding..." : "Add Invite"}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Invites Table */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faUsers} />
            All Invites ({stats.total})
          </h3>
          <div className="flex-row">
            <div className="search-box">
              <FontAwesomeIcon icon={faSearch} />
              <input
                type="text"
                placeholder="Search by email or username..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyUp={handleSearch}
              />
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="btn btn-sm btn-outline"
              title="Refresh"
            >
              <FontAwesomeIcon
                className={`w-4 h-4 inline ${refreshing ? "animate-spin" : ""}`}
                icon={faSync}
              />{" "}
              Refresh
            </button>
          </div>
        </div>

        <div className="card-body">
          {invites.length > 0 ? (
            <div className="table-responsive">
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Discord User</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {invites.map((invite) => (
                    <tr key={invite.id}>
                      <td>#{invite.id}</td>
                      <td>
                        <span className="email-icon">
                          <FontAwesomeIcon
                            icon={faEnvelope}
                            className="w-4 h-4"
                          />
                        </span>
                        {invite.email}
                      </td>
                      <td>
                        <span className="discord-icon">
                          <svg
                            className="w-4 h-4"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                          >
                            <path d="M20.317 4.492c-1.53-.69-3.17-1.2-4.885-1.49a.075.075 0 0 0-.079.036c-.21.369-.444.85-.608 1.23a18.566 18.566 0 0 0-5.487 0 12.36 12.36 0 0 0-.617-1.23A.077.077 0 0 0 8.562 3c-1.714.29-3.354.8-4.885 1.491a.07.07 0 0 0-.032.027C.533 9.093-.32 13.555.099 17.961a.08.08 0 0 0 .031.055 20.03 20.03 0 0 0 5.993 2.98.078.078 0 0 0 .084-.026 13.83 13.83 0 0 0 1.226-1.963.074.074 0 0 0-.041-.104 13.201 13.201 0 0 1-1.872-.878.075.075 0 0 1-.008-.125c.126-.093.252-.19.372-.287a.075.075 0 0 1 .078-.01c3.927 1.764 8.18 1.764 12.061 0a.075.075 0 0 1 .079.009c.12.098.245.195.372.288a.075.075 0 0 1-.006.125c-.598.344-1.22.635-1.873.877a.075.075 0 0 0-.041.105c.36.687.772 1.341 1.225 1.962a.077.077 0 0 0 .084.028 19.963 19.963 0 0 0 6.002-2.981.076.076 0 0 0 .032-.054c.5-5.094-.838-9.52-3.549-13.442a.06.06 0 0 0-.031-.028zM8.02 15.278c-1.182 0-2.157-1.069-2.157-2.38 0-1.312.956-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.956 2.38-2.157 2.38zm7.975 0c-1.183 0-2.157-1.069-2.157-2.38 0-1.312.955-2.38 2.157-2.38 1.21 0 2.176 1.077 2.157 2.38 0 1.312-.946 2.38-2.157 2.38z" />
                          </svg>
                        </span>
                        {invite.discord_user}
                      </td>
                      <td>
                        {invite.status === "active" && (
                          <span className="badge badge-success">Active</span>
                        )}
                        {invite.status === "expired" && (
                          <span className="badge badge-secondary">Expired</span>
                        )}
                        {invite.status === "revoked" && (
                          <span className="badge badge-warning">Revoked</span>
                        )}
                        {invite.status === "removed" && (
                          <span className="badge badge-danger">Removed</span>
                        )}
                        {!["active", "expired", "revoked", "removed"].includes(
                          invite.status
                        ) && (
                          <span className="badge badge-secondary">
                            {invite.status}
                          </span>
                        )}
                      </td>
                      <td>
                        {invite.created_at
                          ? invite.created_at.substring(0, 10)
                          : "-"}
                      </td>
                      <td>
                        <button
                          onClick={() => handleRemoveInvite(invite.id)}
                          className="btn btn-sm btn-danger"
                          title="Remove"
                        >
                          <FontAwesomeIcon icon={faTrash} className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <FontAwesomeIcon
                icon={faUserPlus}
                className="w-16 h-16 mx-auto text-text-muted mb-4"
              />
              <h3>No invites found</h3>
              <p>
                {searchQuery
                  ? "No invites match your search."
                  : "Start by adding a new Plex invitation above."}
              </p>
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
                invites
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
