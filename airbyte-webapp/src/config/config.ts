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

console.log(newStaticConfig);

// OSS config providers (from top to bottom, each level overwriting the previous)
//
// const defaultConfig = {
//   segment: { enabled: true, token: "" },
//   healthCheckInterval: 20000,
//   version: "dev",
//   apiUrl: `${window.location.protocol}//${window.location.hostname}:8001/api`,
//   connectorBuilderApiUrl: `${window.location.protocol}//${window.location.hostname}:8003`,
//   integrationUrl: "/docs",
//   oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
// };

// const envConfigProvider: ConfigProvider = async () => {
//   return {
//     apiUrl: process.env.REACT_APP_API_URL,
//     integrationUrl: process.env.REACT_APP_INTEGRATION_DOCS_URLS,
//     segment: {
//       token: process.env.REACT_APP_SEGMENT_TOKEN,
//     },
//   };
// };

// const windowConfigProvider: ConfigProvider = async () => {
//   return {
//     segment: {
//       enabled: isDefined(window.TRACKING_STRATEGY) ? window.TRACKING_STRATEGY === "segment" : undefined,
//       token: window.SEGMENT_TOKEN,
//     },
//     apiUrl: window.API_URL,
//     connectorBuilderApiUrl: window.CONNECTOR_BUILDER_API_URL,
//     version: window.AIRBYTE_VERSION,
//     // cloud only start
//     // TODO: remove when infra team supports proper webapp building
//     cloud: window.CLOUD === "true",
//     // cloud only end
//   };
// };
