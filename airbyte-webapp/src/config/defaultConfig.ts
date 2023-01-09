import { Config } from "./types";

const defaultConfig: Config = {
  segment: { enabled: true, token: "" },
  healthCheckInterval: 20000,
  version: "dev",
  apiUrl: `${window.location.protocol}//${window.location.hostname}:8001/api`,
  connectorBuilderApiUrl: `${window.location.protocol}//${window.location.hostname}:8003`,
  integrationUrl: "/docs",
  oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
};

export { defaultConfig };
