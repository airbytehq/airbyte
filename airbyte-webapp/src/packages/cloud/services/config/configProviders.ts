import type { CloudConfig } from "./types";

import type { ConfigProvider } from "config/types";

const cloudWindowConfigProvider: ConfigProvider<CloudConfig> = async () => {
  return {
    intercom: {
      appId: window.REACT_APP_INTERCOM_APP_ID,
    },
    firebase: {
      apiKey: window.FIREBASE_API_KEY,
      authDomain: window.FIREBASE_AUTH_DOMAIN,
      authEmulatorHost: window.FIREBASE_AUTH_EMULATOR_HOST,
    },
    cloudApiUrl: window.CLOUD_API_URL,
    launchDarkly: window.LAUNCHDARKLY_KEY,
  };
};

const cloudEnvConfigProvider: ConfigProvider<CloudConfig> = async () => {
  return {
    cloudApiUrl: process.env.REACT_APP_CLOUD_API_URL,
    cloudPublicApiUrl: process.env.REACT_APP_CLOUD_PUBLIC_API_URL,
    firebase: {
      apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
      authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
      authEmulatorHost: process.env.REACT_APP_FIREBASE_AUTH_EMULATOR_HOST,
    },
    intercom: {
      appId: process.env.REACT_APP_INTERCOM_APP_ID,
    },
    launchDarkly: process.env.REACT_APP_LAUNCHDARKLY_KEY,
  };
};

export { cloudWindowConfigProvider, cloudEnvConfigProvider };
