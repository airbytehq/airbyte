import type { CloudConfig } from "./types";

import type { ConfigProvider } from "config/types";

const CONFIG_PATH = "/config.json";

const fileConfigProvider: ConfigProvider<CloudConfig> = async () => {
  const response = await fetch(CONFIG_PATH);

  if (response.ok) {
    try {
      const config = await response.json();

      return config;
    } catch (e) {
      console.error("error occurred while parsing the json config");
      return {};
    }
  }

  return {};
};

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

export { fileConfigProvider, cloudWindowConfigProvider, cloudEnvConfigProvider };
