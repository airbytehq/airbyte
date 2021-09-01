import { Config } from "./types";
import { uiConfig } from "./uiConfig";

const defaultConfig: Config = {
  ui: uiConfig,
  fullstory: {
    orgId: "",
  },
  segment: { enabled: true, token: "" },
  healthCheckInterval: 10000,
  openreplay: {
    obscureTextEmails: false,
    obscureInputEmails: false,
    revID: "",
    projectID: -1,
  },
  papercups: {
    baseUrl: "https://app.papercups.io",
    enableStorytime: false,
    accountId: "",
  },
  version: "",
  apiUrl: `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`,
  isDemo: false,
};

export { defaultConfig };
