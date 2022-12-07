import { Config } from "./types";

export const newStaticConfig: Config = {
  segment: {
    token: process.env.REACT_APP_SEGMENT_TOKEN ?? window.SEGMENT_TOKEN,
    enabled: window.TRACKING_STRATEGY === "segment",
  },
  apiUrl:
    window.API_URL ??
    process.env.REACT_APP_API_URL ??
    `${window.location.protocol}//${window.location.hostname}:8001/api`,
  connectorBuilderApiUrl: "string",
  oauthRedirectUrl: "string",
  healthCheckInterval: 20000,
  version: window.AIRBYTE_VERSION ?? "dev",
  integrationUrl: "string",
  launchDarkly: "string",
  // Cloud-only values:
  cloudApiUrl: process.env.REACT_APP_CLOUD_API_URL ?? window.CLOUD_API_URL,
  firebase: {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY ?? window.FIREBASE_API_KEY,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN ?? window.FIREBASE_AUTH_DOMAIN,
    authEmulatorHost: process.env.REACT_APP_FIREBASE_AUTH_EMULATOR_HOST ?? window.FIREBASE_AUTH_EMULATOR_HOST,
  },
  intercom: {
    appId: process.env.REACT_APP_INTERCOM_APP_ID,
  },
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
