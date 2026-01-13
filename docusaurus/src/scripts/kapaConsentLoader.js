import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";

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

function loadKapaScript() {
  if (kapaLoaded) return;
  kapaLoaded = true;

  const script = document.createElement("script");
  script.src = KAPA_CONFIG.src;
  script.async = true;

  Object.entries(KAPA_CONFIG).forEach(([key, value]) => {
    if (key !== "src") {
      script.setAttribute(key, value);
    }
  });

  document.head.appendChild(script);
  showAskAiButton();
}

function showAskAiButton() {
  const buttons = document.querySelectorAll(".kapa-ai-trigger");
  buttons.forEach((button) => {
    button.style.display = "inline-flex";
  });
}

function hideAskAiButton() {
  const buttons = document.querySelectorAll(".kapa-ai-trigger");
  buttons.forEach((button) => {
    button.style.display = "none";
  });
}

function checkOsanoConsent() {
  if (typeof window.Osano !== "undefined" && window.Osano.cm) {
    const consent = window.Osano.cm.getConsent();
    if (consent && consent.PERSONALIZATION === "ACCEPT") {
      consentGranted = true;
      loadKapaScript();
      return true;
    }
  }
  return false;
}

function setupOsanoListeners() {
  if (typeof window.Osano === "function") {
    window.Osano("onPersonalization", () => {
      consentGranted = true;
      loadKapaScript();
    });

    window.Osano("onInitialized", () => {
      checkOsanoConsent();
    });
  } else if (typeof window.Osano !== "undefined" && window.Osano.cm) {
    window.Osano.cm.addEventListener(
      "osano-cm-consent-changed",
      checkOsanoConsent
    );
    checkOsanoConsent();
  }
}

function initKapaLoader() {
  hideAskAiButton();

  if (typeof window.Osano === "undefined") {
    consentGranted = true;
    loadKapaScript();
    return;
  }

  setupOsanoListeners();

  if (!checkOsanoConsent()) {
    const checkInterval = setInterval(() => {
      if (checkOsanoConsent() || consentGranted) {
        clearInterval(checkInterval);
      }
    }, 500);

    setTimeout(() => {
      clearInterval(checkInterval);
    }, 10000);
  }
}

if (ExecutionEnvironment.canUseDOM) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initKapaLoader);
  } else {
    initKapaLoader();
  }
}

export const onRouteDidUpdate = () => {
  if (consentGranted && kapaLoaded) {
    showAskAiButton();
  } else {
    hideAskAiButton();
  }
};
