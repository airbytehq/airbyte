import { AirbyteWebappConfig } from "./types";

export const newStaticConfig: AirbyteWebappConfig = {
  segment: {
    token: window.SEGMENT_TOKEN ?? process.env.REACT_APP_SEGMENT_TOKEN ?? "",
    enabled: window.TRACKING_STRATEGY === "segment",
  },
  apiUrl:
    window.API_URL ??
    process.env.REACT_APP_API_URL ??
    `${window.location.protocol}//${window.location.hostname}:8001/api`,
  connectorBuilderApiUrl:
    process.env.REACT_APP_CONNECTOR_BUILDER_API_URL ?? `${window.location.protocol}//${window.location.hostname}:8003`,
  healthCheckInterval: 20000,
  version: window.AIRBYTE_VERSION ?? "dev",
  integrationUrl: process.env.REACT_APP_INTEGRATION_DOCS_URLS ?? "/docs",
};
