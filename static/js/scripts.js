// Custom JavaScript for Zambia Tennis Association website
// This file is intentionally left mostly empty.  You can add interactive
// scripts here as you expand the site.

// Example: automatically close alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});