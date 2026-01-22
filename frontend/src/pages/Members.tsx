import { useEffect, useState } from "react";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUsers,
  faShield,
  faSearch,
  faSync,
  faUser,
  faCircle,
  faTimes,
  faPlus,
  faChevronLeft,
  faChevronRight,
  faCheck,
} from "@fortawesome/free-solid-svg-icons";

interface RoleInfo {
  id: string;
  name: string;
  color: string;
}

interface MemberItem {
  id: string;
  name: string;
  display_name: string;
  avatar: string | null;
  status: string;
  roles: RoleInfo[];
}

interface RoleItem {
  id: string;
  name: string;
  color: string;
  position: number;
  mentionable: boolean;
  hoist: boolean;
  member_count: number;
}

interface MembersStats {
  total_members: number;
  total_roles: number;
}

interface MembersData {
  members: MemberItem[];
  roles: RoleItem[];
  stats: MembersStats;
  total_pages: number;
}

export default function Members() {
  const [activeTab, setActiveTab] = useState<"members" | "roles">("members");
  const [data, setData] = useState<MembersData | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [roleSearch, setRoleSearch] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedMember, setSelectedMember] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [selectedRole, setSelectedRole] = useState("");
  const perPage = 10;

  useEffect(() => {
    if (loading) {
      fetchMembers();
    } else {
      fetchMembers(false);
    }
  }, [page, search]);

  const fetchMembers = async (showLoader = false) => {
    try {
      if (showLoader) {
        setLoading(true);
      }
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
      });
      if (search) {
        params.append("search", search);
      }
      const response = await api.get(`/members/?${params.toString()}`);
      setData(response.data);
    } catch (error) {
      console.error("Error fetching members:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setPage(1);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchMembers(false);
  };

  const openAddRoleModal = (memberId: string, memberName: string) => {
    setSelectedMember({ id: memberId, name: memberName });
    setSelectedRole("");
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedMember(null);
    setSelectedRole("");
  };

  const confirmAddRole = async () => {
    if (!selectedMember || !selectedRole) {
      alert("Please select a role");
      return;
    }

    try {
      await api.post("/members/member/add-role", {
        user_id: selectedMember.id,
        role_id: selectedRole,
      });
      alert("Role added successfully");
      closeModal();
      fetchMembers();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to add role");
    }
  };

  const removeRole = async (memberId: string, roleId: string) => {
    if (!confirm("Are you sure you want to remove this role?")) {
      return;
    }

    try {
      await api.post("/members/member/remove-role", {
        user_id: memberId,
        role_id: roleId,
      });
      alert("Role removed successfully");
      fetchMembers();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to remove role");
    }
  };

  const filteredRoles = data?.roles.filter((role) =>
    role.name.toLowerCase().includes(roleSearch.toLowerCase())
  );

  if (loading && !data) {
    return <LoadingSpinner message="Loading members..." />;
  }

  return (
    <div className="members-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faUsers} /> Members & Roles
        </h1>
        <p className="subtitle">Manage member roles and permissions</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon members">
            <FontAwesomeIcon icon={faUsers} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data?.stats.total_members || 0}</div>
            <div className="stat-label">Total Members</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon roles">
            <FontAwesomeIcon icon={faShield} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data?.stats.total_roles || 0}</div>
            <div className="stat-label">Total Roles</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab-button ${activeTab === "members" ? "active" : ""}`}
          onClick={() => setActiveTab("members")}
        >
          <FontAwesomeIcon icon={faUsers} /> Members
        </button>
        <button
          className={`tab-button ${activeTab === "roles" ? "active" : ""}`}
          onClick={() => setActiveTab("roles")}
        >
          <FontAwesomeIcon icon={faShield} /> Roles
        </button>
      </div>

      {/* Members Tab */}
      {activeTab === "members" && (
        <div className="tab-content active">
          <div className="card">
            <div className="card-header">
              <h3>
                <FontAwesomeIcon icon={faUsers} /> Guild Members
              </h3>
              <div className="flex-row">
                <div className="search-box">
                  <FontAwesomeIcon icon={faSearch} />
                  <input
                    type="text"
                    placeholder="Search members..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyPress={handleSearch}
                  />
                </div>
                <button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="btn btn-sm btn-outline"
                >
                  <FontAwesomeIcon
                    icon={faSync}
                    className={`w-4 h-4 inline ${
                      refreshing ? "animate-spin" : ""
                    }`}
                  />{" "}
                  Refresh
                </button>
              </div>
            </div>
            <div className="card-body">
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Member</th>
                      <th>Status</th>
                      <th>Roles</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data?.members.map((member) => (
                      <tr key={member.id}>
                        <td>
                          <div className="member-info">
                            {member.avatar ? (
                              <img
                                src={member.avatar}
                                alt={member.name}
                                className="member-avatar"
                              />
                            ) : (
                              <div className="member-avatar-placeholder">
                                <FontAwesomeIcon icon={faUser} />
                              </div>
                            )}
                            <div>
                              <div className="member-name">{member.name}</div>
                              <div className="member-id">ID: {member.id}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span
                            className={`status-badge status-${member.status}`}
                          >
                            <FontAwesomeIcon icon={faCircle} /> {member.status}
                          </span>
                        </td>
                        <td>
                          <div className="role-badges">
                            {member.roles.map((role) => (
                              <span
                                key={role.id}
                                className="role-badge"
                                style={{ backgroundColor: role.color }}
                              >
                                {role.name}
                                <button
                                  className="role-remove-btn"
                                  onClick={() => removeRole(member.id, role.id)}
                                  title="Remove role"
                                >
                                  <FontAwesomeIcon icon={faTimes} />
                                </button>
                              </span>
                            ))}
                          </div>
                        </td>
                        <td>
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() =>
                              openAddRoleModal(member.id, member.name)
                            }
                          >
                            <FontAwesomeIcon icon={faPlus} /> Add Role
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {data && data.total_pages > 1 && (
              <div className="card-footer">
                <div className="pagination-container">
                  <div className="pagination-info">
                    Showing {(page - 1) * perPage + 1} -{" "}
                    {Math.min(page * perPage, data.stats.total_members)} of{" "}
                    {data.stats.total_members} members
                  </div>
                  <div className="pagination">
                    {page > 1 && (
                      <button
                        className="btn btn-sm btn-outline"
                        onClick={() => setPage(page - 1)}
                      >
                        <FontAwesomeIcon icon={faChevronLeft} /> Previous
                      </button>
                    )}

                    {Array.from({ length: data.total_pages }, (_, i) => i + 1)
                      .filter((p) => {
                        if (p === 1 || p === data.total_pages) return true;
                        if (p >= page - 2 && p <= page + 2) return true;
                        return false;
                      })
                      .map((p, idx, arr) => {
                        if (idx > 0 && p - arr[idx - 1] > 1) {
                          return (
                            <span key={`ellipsis-${p}`}>
                              <span className="btn btn-sm btn-outline disabled">
                                ...
                              </span>
                              <button
                                className={`btn btn-sm ${
                                  p === page ? "btn-primary" : "btn-outline"
                                }`}
                                onClick={() => setPage(p)}
                              >
                                {p}
                              </button>
                            </span>
                          );
                        }
                        return (
                          <button
                            key={p}
                            className={`btn btn-sm ${
                              p === page ? "btn-primary" : "btn-outline"
                            }`}
                            onClick={() => setPage(p)}
                          >
                            {p}
                          </button>
                        );
                      })}

                    {page < data.total_pages && (
                      <button
                        className="btn btn-sm btn-outline"
                        onClick={() => setPage(page + 1)}
                      >
                        Next <FontAwesomeIcon icon={faChevronRight} />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Roles Tab */}
      {activeTab === "roles" && (
        <div className="tab-content active">
          <div className="card">
            <div className="card-header">
              <h3>
                <FontAwesomeIcon icon={faShield} /> Server Roles
              </h3>
              <div className="search-box">
                <FontAwesomeIcon icon={faSearch} />
                <input
                  type="text"
                  placeholder="Search roles..."
                  value={roleSearch}
                  onChange={(e) => setRoleSearch(e.target.value)}
                />
              </div>
            </div>
            <div className="card-body">
              <div className="roles-grid">
                {filteredRoles?.map((role) => (
                  <div key={role.id} className="role-card">
                    <div
                      className="role-card-header"
                      style={{ borderLeft: `4px solid ${role.color}` }}
                    >
                      <div className="role-name" style={{ color: role.color }}>
                        <FontAwesomeIcon icon={faShield} />
                        {role.name}
                      </div>
                      <div className="role-member-count">
                        <FontAwesomeIcon icon={faUsers} /> {role.member_count}{" "}
                        members
                      </div>
                    </div>
                    <div className="role-card-body">
                      <div className="role-details">
                        <div className="role-detail">
                          <span className="label">Position:</span>
                          <span className="value">{role.position}</span>
                        </div>
                        <div className="role-detail">
                          <span className="label">Mentionable:</span>
                          <span className="value">
                            {role.mentionable ? (
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
                          </span>
                        </div>
                        <div className="role-detail">
                          <span className="label">Hoisted:</span>
                          <span className="value">
                            {role.hoist ? (
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
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Role Modal */}
      {showModal && (
        <div
          className="modal show"
          onClick={(e) => {
            if (e.target === e.currentTarget) closeModal();
          }}
        >
          <div className="modal-content">
            <div className="modal-header">
              <h3>
                <FontAwesomeIcon icon={faPlus} /> Add Role to{" "}
                {selectedMember?.name}
              </h3>
              <button className="modal-close" onClick={closeModal}>
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="roleSelect">Select Role:</label>
                <select
                  id="roleSelect"
                  className="form-control"
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                >
                  <option value="">-- Select a role --</option>
                  {data?.roles.map((role) => (
                    <option
                      key={role.id}
                      value={role.id}
                      style={{ color: role.color }}
                    >
                      {role.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={closeModal}>
                <FontAwesomeIcon icon={faTimes} /> Cancel
              </button>
              <button className="btn btn-primary" onClick={confirmAddRole}>
                <FontAwesomeIcon icon={faCheck} /> Add Role
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
