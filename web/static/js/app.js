// Discord Bot Manager - Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Initialize
  initSidebarToggle();
  initCurrentTime();
  initAlertDismiss();
  initVersionChecker();
});

// Sidebar Toggle
function initSidebarToggle() {
  const toggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");

  if (toggle && sidebar) {
    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("active");
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener("click", (e) => {
      if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
          sidebar.classList.remove("active");
        }
      }
    });
  }
}

// Current Time
function initCurrentTime() {
  const timeElement = document.getElementById("currentTime");

  if (timeElement) {
    function updateTime() {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");
      timeElement.textContent = `${hours}:${minutes}`;
    }

    updateTime();
    setInterval(updateTime, 60000); // Update every minute
  }
}

// Alert Dismiss
function initAlertDismiss() {
  const alerts = document.querySelectorAll(".alert-dismissible");

  alerts.forEach((alert) => {
    const closeBtn = alert.querySelector(".close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.style.animation = "fadeOut 0.3s ease-out";
        setTimeout(() => {
          alert.remove();
        }, 300);
      });
    }
  });
}

// Version Checker with Badge
function initVersionChecker() {
  const badge = document.getElementById("versionBadge");

  if (badge) {
    // Check version on load
    checkVersion();

    // Make version container clickable to refresh
    const versionContainer = document.getElementById("versionContainer");
    if (versionContainer) {
      versionContainer.style.cursor = "pointer";
      versionContainer.addEventListener("click", checkVersion);
    }
  }
}

async function checkVersion() {
  const badge = document.getElementById("versionBadge");
  if (!badge) return;

  // Show loading state
  badge.style.display = "inline-block";
  badge.className = "badge badge-info ms-2";
  badge.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

  try {
    const response = await fetch("/api/version");
    const data = await response.json();

    if (data.error) {
      badge.className = "badge badge-warning ms-2";
      badge.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
      badge.title = "Could not check for updates";
    } else if (data.is_update_available) {
      badge.className = "badge badge-warning ms-2";
      badge.innerHTML = '<i class="fas fa-arrow-up"></i> Update';
      badge.title = `Update available: v${data.remote}`;
      badge.style.cursor = "pointer";
      badge.onclick = () =>
        window.open(
          "https://github.com/cyb3rgh05t/discord-bot/releases/latest",
          "_blank"
        );
    } else {
      badge.className = "badge badge-success ms-2";
      badge.innerHTML = '<i class="fas fa-check"></i> Up to date';
      badge.title = "You are running the latest version";
    }
  } catch (error) {
    console.error("Error checking version:", error);
    badge.className = "badge badge-danger ms-2";
    badge.innerHTML = '<i class="fas fa-times"></i>';
    badge.title = "Error checking for updates";
  }
}

// Update Checker (legacy)
function initUpdateChecker() {
  const checkBtn = document.getElementById("checkUpdates");

  if (checkBtn) {
    checkBtn.addEventListener("click", async () => {
      const originalText = checkBtn.innerHTML;
      checkBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
      checkBtn.disabled = true;

      try {
        const response = await fetch("/api/check-updates");
        const data = await response.json();

        if (data.update_available) {
          showNotification(
            "success",
            `Update available: ${data.latest_version}`
          );
        } else {
          showNotification("info", "You are running the latest version");
        }
      } catch (error) {
        console.error("Error checking updates:", error);
        showNotification("danger", "Failed to check for updates");
      } finally {
        checkBtn.innerHTML = originalText;
        checkBtn.disabled = false;
      }
    });
  }
}

// Show Notification
function showNotification(type, message) {
  const flashContainer =
    document.querySelector(".flash-messages") || createFlashContainer();

  const alert = document.createElement("div");
  alert.className = `alert alert-${type} alert-dismissible`;
  alert.innerHTML = `
        <button type="button" class="close">
            <i class="fas fa-times"></i>
        </button>
        <i class="fas fa-${getIconForType(type)}"></i>
        ${message}
    `;

  flashContainer.appendChild(alert);

  // Auto dismiss after 5 seconds
  setTimeout(() => {
    alert.style.animation = "fadeOut 0.3s ease-out";
    setTimeout(() => alert.remove(), 300);
  }, 5000);

  // Manual dismiss
  alert.querySelector(".close").addEventListener("click", () => {
    alert.style.animation = "fadeOut 0.3s ease-out";
    setTimeout(() => alert.remove(), 300);
  });
}

function createFlashContainer() {
  const container = document.createElement("div");
  container.className = "flash-messages";
  document
    .querySelector(".content-wrapper")
    .insertBefore(
      container,
      document.querySelector(".content-wrapper").firstChild
    );
  return container;
}

function getIconForType(type) {
  const icons = {
    success: "check-circle",
    danger: "exclamation-circle",
    warning: "exclamation-triangle",
    info: "info-circle",
  };
  return icons[type] || "info-circle";
}

// Utility: Confirm Action
function confirmAction(message, callback) {
  if (confirm(message)) {
    callback();
  }
}

// Utility: Format Bytes
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

// Utility: Format Duration
function formatDuration(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);

  return parts.join(" ") || "0m";
}

// Utility: Debounce
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Export utilities
window.BotManager = {
  showNotification,
  confirmAction,
  formatBytes,
  formatDuration,
  debounce,
};

// Add fadeOut animation
const style = document.createElement("style");
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);
