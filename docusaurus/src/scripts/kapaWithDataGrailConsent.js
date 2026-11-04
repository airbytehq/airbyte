/**
 * Kapa AI integration with DataGrail consent management.
 *
 * This module handles loading the Kapa AI widget only after DataGrail consent is received.
 * If DataGrail is not present (e.g., on Vercel preview deployments), Kapa loads immediately.
 * If DataGrail is present but consent is not given, the Ask AI button is hidden and Kapa is not loaded.
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

/**
 * DataGrail consent category for analytics/performance tags, as configured in the
 * shared Airbyte container.
 * @see https://docs.datagrail.io/docs/consent/banner/banner-api/
 */
const ANALYTICS_CATEGORY = "performance";

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
 * Check whether the visitor has granted analytics consent via DataGrail
 */
function hasAnalyticsConsent() {
  return Boolean(
    window.DG_BANNER_API &&
    typeof window.DG_BANNER_API.categoryEnabled === "function" &&
    window.DG_BANNER_API.categoryEnabled(ANALYTICS_CATEGORY),
  );
}

/**
 * Apply the current consent state: load Kapa if consented, hide the button otherwise
 */
function applyConsentState() {
  if (hasAnalyticsConsent()) {
    loadKapaScript();
  } else {
    hideAskAiButton();
  }
}

/**
 * Register DataGrail consent callbacks. DataGrail processes the window.dgEvent queue,
 * so callbacks can be registered before or after the consent script loads.
 * @see https://docs.datagrail.io/docs/consent/banner/banner-api/
 */
function registerConsentCallbacks() {
  window.dgEvent = window.dgEvent || [];
  window.dgEvent.push({
    event: "initial_preference_callback",
    params: applyConsentState,
  });
  window.dgEvent.push({
    event: "preference_callback",
    params: applyConsentState,
  });
}

/**
 * Check if consent has been granted (for use by React components)
 */
export function hasKapaConsent() {
  return consentGranted || !isDataGrailPresent();
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
 * Check if DataGrail is present
 */
function isDataGrailPresent() {
  return (
    typeof window !== "undefined" && typeof window.DG_BANNER_API !== "undefined"
  );
}

/**
 * Poll for DataGrail's presence and initialize once found.
 * DataGrail is injected via Cloudflare and may load after our script runs.
 * We poll for up to 5 seconds before assuming DataGrail is not present.
 */
function pollForDataGrailAndInit() {
  const maxAttempts = 10;
  const pollInterval = 500; // 500ms between attempts
  let attempts = 0;

  registerConsentCallbacks();

  function checkAndInit() {
    attempts++;

    if (isDataGrailPresent()) {
      applyConsentState();
    } else if (attempts < maxAttempts) {
      setTimeout(checkAndInit, pollInterval);
    } else {
      // DataGrail not found after polling, assume it's not present (e.g., Vercel preview)
      loadKapaScript();
    }
  }

  checkAndInit();
}

// Initialize when the DOM is ready
if (typeof window !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", pollForDataGrailAndInit);
  } else {
    // DOM is already ready, start polling for DataGrail
    pollForDataGrailAndInit();
  }
}

export default pollForDataGrailAndInit;
