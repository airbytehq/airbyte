import { Config } from "./types";

export const newStaticConfig: Config = {
  segment: {
    token: process.env.REACT_APP_SEGMENT_TOKEN || window.SEGMENT_TOKEN,
    enabled: window.TRACKING_STRATEGY === "segment",
  },
  apiUrl: "string",
  connectorBuilderApiUrl: "string",
  oauthRedirectUrl: "string",
  healthCheckInterval: 1,
  version: "string",
  integrationUrl: "string",
  launchDarkly: "string",
  // Cloud-only values:
  cloudApiUrl: process.env.REACT_APP_CLOUD_API_URL || window.CLOUD_API_URL,
  firebase: {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY || window.FIREBASE_API_KEY,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || window.FIREBASE_AUTH_DOMAIN,
    authEmulatorHost: process.env.REACT_APP_FIREBASE_AUTH_EMULATOR_HOST || window.FIREBASE_AUTH_EMULATOR_HOST,
  },
  intercom: {
    appId: process.env.REACT_APP_INTERCOM_APP_ID,
  },
};

console.log(newStaticConfig);
