import { Config } from "./types";

const defaultConfig: Config = {
  segment: { enabled: true, token: "" },
  healthCheckInterval: 20000,
  version: "dev",
  apiUrl: `http://${window.location.hostname}:8001/api`,
  connectorBuilderApiUrl: `http://${window.location.hostname}:8003`,
  integrationUrl: "/docs",
  oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
};

export { defaultConfig };
