import { defaultConfig as coreDefaultConfig, useConfig as useCoreConfig } from "config";

import { CloudConfig, CloudConfigExtension } from "./types";

export function useConfig(): CloudConfig {
  return useCoreConfig<CloudConfig>();
}

const cloudConfigExtensionDefault: CloudConfigExtension = {
  cloudApiUrl: "",
  cloudPublicApiUrl: "/cloud_api",
  firebase: {
    apiKey: "",
    authDomain: "",
    authEmulatorHost: "",
  },
  intercom: {
    appId: "",
  },
};

export const defaultConfig: CloudConfig = {
  ...coreDefaultConfig,
  ...cloudConfigExtensionDefault,
};

export * from "./configProviders";
export * from "./types";

// export const newStaticConfig: Config = {
//   segment: {
//     token: window.SEGMENT_TOKEN ?? process.env.REACT_APP_SEGMENT_TOKEN ?? "",
//     enabled: window.TRACKING_STRATEGY === "segment",
//   },
//   apiUrl:
//     window.API_URL ??
//     process.env.REACT_APP_API_URL ??
//     `${window.location.protocol}//${window.location.hostname}:8001/api`,
//   connectorBuilderApiUrl: process.env.REACT_APP_CONNECTOR_BUILDER_API_URL ?? "",
//   oauthRedirectUrl: "string",
//   healthCheckInterval: 20000,
//   version: window.AIRBYTE_VERSION ?? "dev",
//   integrationUrl: process.env.REACT_APP_INTEGRATION_DOCS_URLS ?? "/docs",
//   launchDarkly: "string",
//   // Cloud-only values:
//   cloudApiUrl: process.env.REACT_APP_CLOUD_API_URL ?? window.CLOUD_API_URL,
//   firebase: {
//     apiKey: process.env.REACT_APP_FIREBASE_API_KEY ?? window.FIREBASE_API_KEY,
//     authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN ?? window.FIREBASE_AUTH_DOMAIN,
//     authEmulatorHost: process.env.REACT_APP_FIREBASE_AUTH_EMULATOR_HOST ?? window.FIREBASE_AUTH_EMULATOR_HOST,
//   },
//   intercom: {
//     appId: process.env.REACT_APP_INTERCOM_APP_ID,
//   },
// };
