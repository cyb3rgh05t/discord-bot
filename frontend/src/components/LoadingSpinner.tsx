import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";

interface LoadingSpinnerProps {
  message?: string;
  fullPage?: boolean;
}

export default function LoadingSpinner({
  message = "Loading...",
  fullPage = true,
}: LoadingSpinnerProps) {
  if (fullPage) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">
          <FontAwesomeIcon icon={faSpinner} className="spinner-icon" spin />
          <p className="loading-message">{message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="loading-spinner-inline">
      <FontAwesomeIcon icon={faSpinner} className="spinner-icon-small" spin />
      <span className="loading-message-small">{message}</span>
    </div>
  );
}
