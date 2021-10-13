import { Config } from "./types";
import { uiConfig } from "./uiConfig";

const defaultConfig: Config = {
  ui: uiConfig,
  fullstory: {
    orgId: "",
  },
  segment: { enabled: true, token: "" },
  healthCheckInterval: 10000,
  version: "",
  apiUrl: `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`,
  oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
  isDemo: false,
};

export { defaultConfig };
