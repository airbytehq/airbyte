/**
 * Kapa AI integration with Osano consent management.
 * 
 * This module handles loading the Kapa AI widget only after Osano consent is received.
 * If Osano is not present (e.g., on Vercel preview deployments), Kapa loads immediately.
 * If Osano is present but consent is not given, the Ask AI button is hidden and Kapa is not loaded.
 */

const KAPA_CONFIG = {
  src: "https://widget.kapa.ai/kapa-widget.bundle.js",
  "data-website-id": "894ff9ab-1c3d-48d3-a014-aa0f52d0b113",
  "data-project-name": "Airbyte",
  "data-project-color": "#615EFF",
  "data-project-logo": "https://docs.airbyte.com/img/favicon.png",
  "data-modal-title": "Ask anything about Airbyte",
  "data-modal-disclaimer":
    "AI can make mistakes. Verify critical information. Using the MCP server requires logging in with Google.",
  "data-modal-example-questions":
    "What's Airbyte?,How do I try Airbyte Cloud?,Help me build a connector,Help me troubleshoot something",
  "data-button-hide": "true",
  "data-modal-override-open-selector-ask-ai": ".kapa-ai-trigger",
  "data-mcp-enabled": "true",
  "data-mcp-server-url": "https://airbyte.mcp.kapa.ai",
  "data-modal-x-offset": "0.5rem",
  "data-modal-y-offset": "0.5rem",
  "data-modal-with-overlay": "false",
  "data-modal-lock-scroll": "false",
  "data-modal-inner-max-width": "500px",
  "data-modal-inner-flex-direction": "column",
  "data-modal-inner-justify-content": "end",
  "data-modal-inner-position-left": "auto",
  "data-modal-inner-position-top": "0",
  "data-modal-inner-position-right": "0",
  "data-modal-inner-position-bottom": "0",
  "data-modal-size": "calc(100vh - 1rem)",
};

let kapaLoaded = false;
let consentGranted = false;

/**
 * Load the Kapa AI script dynamically
 */
function loadKapaScript() {
  if (kapaLoaded) return;

  const script = document.createElement("script");
  script.src = KAPA_CONFIG.src;
  script.async = true;

  // Add all data attributes
  Object.entries(KAPA_CONFIG).forEach(([key, value]) => {
    if (key !== "src") {
      script.setAttribute(key, value);
    }
  });

  document.head.appendChild(script);
  kapaLoaded = true;

  // Show the Ask AI button
  showAskAiButton();
}

/**
 * Show the Ask AI button by removing the hidden class
 */
function showAskAiButton() {
  const buttons = document.querySelectorAll(".kapa-ai-trigger");
  buttons.forEach((button) => {
    button.classList.remove("kapa-ai-hidden");
  });
  consentGranted = true;
}

/**
 * Hide the Ask AI button by adding the hidden class
 */
function hideAskAiButton() {
  const buttons = document.querySelectorAll(".kapa-ai-trigger");
  buttons.forEach((button) => {
    button.classList.add("kapa-ai-hidden");
  });
  consentGranted = false;
}

/**
 * Check if Osano is present and handle consent
 */
function initKapaWithOsanoConsent() {
  // Check if Osano is available
  if (typeof window.Osano !== "undefined" && window.Osano.cm) {
    // Osano is present, check current consent status
    const consent = window.Osano.cm.getConsent();

    // Check if analytics consent is granted (Kapa uses analytics/tracking)
    if (consent && consent.ANALYTICS === "ACCEPT") {
      loadKapaScript();
    } else {
      hideAskAiButton();
    }

    // Listen for consent changes
    window.Osano.cm.addEventListener(
      "osano-cm-consent-changed",
      (newConsent) => {
        if (newConsent.ANALYTICS === "ACCEPT") {
          loadKapaScript();
        } else {
          hideAskAiButton();
        }
      }
    );
  } else if (typeof window.Osano === "function") {
    // Osano pre-load interface is available but not fully loaded yet
    // Use the pre-load interface to listen for initialization
    window.Osano("onInitialized", (consent) => {
      if (consent && consent.ANALYTICS === "ACCEPT") {
        loadKapaScript();
      } else {
        hideAskAiButton();
      }
    });

    window.Osano("onConsentChanged", (newConsent) => {
      if (newConsent.ANALYTICS === "ACCEPT") {
        loadKapaScript();
      } else {
        hideAskAiButton();
      }
    });
  } else {
    // Osano is not present (e.g., Vercel preview, local development)
    // Load Kapa immediately
    loadKapaScript();
  }
}

/**
 * Check if consent has been granted (for use by React components)
 */
export function hasKapaConsent() {
  return consentGranted || !isOsanoPresent();
}

/**
 * Re-apply button visibility state after Docusaurus SPA navigation.
 * This is called by Docusaurus on every route change.
 */
export function onRouteDidUpdate() {
  if (consentGranted) {
    showAskAiButton();
  }
}

/**
 * Check if Osano is present
 */
function isOsanoPresent() {
  return (
    typeof window !== "undefined" &&
    (typeof window.Osano !== "undefined" ||
      (typeof window.Osano === "function" && window.Osano.data))
  );
}

/**
 * Poll for Osano's presence and initialize once found.
 * Osano is injected via Cloudflare and may load after our script runs.
 * We poll for up to 5 seconds before assuming Osano is not present.
 */
function pollForOsanoAndInit() {
  const maxAttempts = 10;
  const pollInterval = 500; // 500ms between attempts
  let attempts = 0;

  function checkAndInit() {
    attempts++;
    const osanoPresent =
      (typeof window.Osano !== "undefined" && window.Osano.cm) ||
      typeof window.Osano === "function";

    if (osanoPresent) {
      initKapaWithOsanoConsent();
    } else if (attempts < maxAttempts) {
      setTimeout(checkAndInit, pollInterval);
    } else {
      // Osano not found after polling, assume it's not present (e.g., Vercel preview)
      initKapaWithOsanoConsent();
    }
  }

  checkAndInit();
}

// Initialize when the DOM is ready
if (typeof window !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", pollForOsanoAndInit);
  } else {
    // DOM is already ready, start polling for Osano
    pollForOsanoAndInit();
  }
}

export default initKapaWithOsanoConsent;
