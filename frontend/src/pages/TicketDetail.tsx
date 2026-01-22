import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faChevronLeft,
  faTicket,
  faUser,
  faHashtag,
  faTag,
  faComments,
  faCalendar,
  faFlag,
  faUserCheck,
  faLock,
  faTimes,
} from "@fortawesome/free-solid-svg-icons";
import api from "../lib/api";

interface TicketData {
  id: number;
  user_id: string;
  username: string;
  channel_id: string;
  type: string;
  ticket_type: string;
  status: string;
  created_at: string;
  closed_at?: string;
  claimed?: boolean;
  claimed_by?: string;
  locked?: boolean;
}

const TicketDetail = () => {
  const { ticketId } = useParams<{ ticketId: string }>();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<TicketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTicketDetails();
  }, [ticketId]);

  const fetchTicketDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/tickets/${ticketId}`);
      if (response.data.success) {
        setTicket(response.data.ticket);
      } else {
        setError(response.data.message || "Ticket not found");
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to fetch ticket details");
    } finally {
      setLoading(false);
    }
  };

  const handleCloseTicket = async () => {
    if (!confirm("Are you sure you want to close this ticket?")) {
      return;
    }

    try {
      const response = await api.post(`/tickets/${ticketId}/close`);
      if (response.data.success) {
        // Refresh ticket details
        fetchTicketDetails();
      } else {
        alert("Error: " + response.data.message);
      }
    } catch (err: any) {
      alert(
        "Error closing ticket: " + (err.response?.data?.message || err.message)
      );
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading ticket details..." />;
  }

  if (error || !ticket) {
    return (
      <div className="error-container">
        <p className="error-message">{error || "Ticket not found"}</p>
        <button
          onClick={() => navigate("/tickets")}
          className="btn btn-primary"
        >
          <FontAwesomeIcon icon={faChevronLeft} />
          Back to Tickets
        </button>
      </div>
    );
  }

  return (
    <div className="ticket-view-page">
      <div className="page-header">
        <div>
          <h1>
            <FontAwesomeIcon icon={faTicket} />
            Ticket #{ticket.id}
          </h1>
          <p className="subtitle">
            <span
              className={`badge ${
                ticket.ticket_type === "plex" ? "badge-info" : "badge-warning"
              }`}
            >
              {ticket.ticket_type.toUpperCase()}
            </span>
            <span
              className={`badge ${
                ticket.status === "open" ? "badge-success" : "badge-secondary"
              }`}
            >
              {ticket.status.toUpperCase()}
            </span>
          </p>
        </div>
        <div className="header-actions">
          <button
            onClick={() => navigate("/tickets")}
            className="btn btn-outline"
          >
            <FontAwesomeIcon icon={faChevronLeft} />
            Back to Tickets
          </button>
          {ticket.status === "open" && (
            <button onClick={handleCloseTicket} className="btn btn-danger">
              <FontAwesomeIcon icon={faTimes} />
              Close Ticket
            </button>
          )}
        </div>
      </div>

      {/* Ticket Details */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faTag} />
            Ticket Information
          </h3>
        </div>
        <div className="card-body">
          <div className="ticket-details-grid">
            <div className="detail-item">
              <label>
                <FontAwesomeIcon icon={faHashtag} />
                Ticket ID
              </label>
              <div className="detail-value">#{ticket.id}</div>
            </div>

            <div className="detail-item">
              <label>
                <FontAwesomeIcon icon={faUser} />
                User
              </label>
              <div className="detail-value">{ticket.username}</div>
            </div>

            <div className="detail-item">
              <label>
                <FontAwesomeIcon icon={faHashtag} />
                User ID
              </label>
              <div className="detail-value">{ticket.user_id}</div>
            </div>

            <div className="detail-item">
              <label>
                <FontAwesomeIcon icon={faTag} />
                Type
              </label>
              <div className="detail-value">{ticket.type || "N/A"}</div>
            </div>

            <div className="detail-item">
              <label>
                <FontAwesomeIcon icon={faComments} />
                Channel ID
              </label>
              <div className="detail-value">{ticket.channel_id}</div>
            </div>

            <div className="detail-item">
              <label>
                <FontAwesomeIcon icon={faCalendar} />
                Created
              </label>
              <div className="detail-value">{ticket.created_at || "N/A"}</div>
            </div>

            <div className="detail-item">
              <label>
                <FontAwesomeIcon icon={faFlag} />
                Status
              </label>
              <div className="detail-value">
                <span
                  className={`badge ${
                    ticket.status === "open"
                      ? "badge-success"
                      : "badge-secondary"
                  }`}
                >
                  {ticket.status.toUpperCase()}
                </span>
              </div>
            </div>

            {ticket.claimed && (
              <div className="detail-item">
                <label>
                  <FontAwesomeIcon icon={faUserCheck} />
                  Claimed By
                </label>
                <div className="detail-value">{ticket.claimed_by || "N/A"}</div>
              </div>
            )}

            {ticket.locked && (
              <div className="detail-item">
                <label>
                  <FontAwesomeIcon icon={faLock} />
                  Locked
                </label>
                <div className="detail-value">
                  <span className="badge badge-warning">
                    <FontAwesomeIcon icon={faLock} />
                    LOCKED
                  </span>
                </div>
              </div>
            )}

            {ticket.closed_at && (
              <div className="detail-item">
                <label>
                  <FontAwesomeIcon icon={faCalendar} />
                  Closed
                </label>
                <div className="detail-value">{ticket.closed_at}</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Discord Channel Link */}
      <div className="card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faComments} />
            Discord Channel
          </h3>
        </div>
        <div className="card-body">
          <p>
            <strong>Channel ID:</strong> {ticket.channel_id}
          </p>
          <p style={{ color: "var(--text-muted)" }}>
            You can view this ticket in Discord by navigating to the channel.
          </p>
        </div>
      </div>

      {/* Actions */}
      {ticket.status === "open" && (
        <div className="card">
          <div className="card-header">
            <h3>Actions</h3>
          </div>
          <div className="card-body">
            <div className="action-buttons">
              <button onClick={handleCloseTicket} className="btn btn-danger">
                <FontAwesomeIcon icon={faTimes} />
                Close Ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TicketDetail;
