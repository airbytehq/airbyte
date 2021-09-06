import { ConfigProvider } from "config/types";
import { CloudConfig } from "./types";

const CONFIG_PATH = "/config.json";

const fileConfigProvider: ConfigProvider<CloudConfig> = async () => {
  const response = await fetch(CONFIG_PATH);

  if (response.ok) {
    try {
      const config = await response.json();

      return config;
    } catch (e) {
      console.error("error occurred while parsing the json config");
    }
  }

  return {};
};

const cloudEnvConfigProvider: ConfigProvider<CloudConfig> = async () => {
  return {
    cloudApiUrl: process.env.REACT_APP_CLOUD_API_URL,
    firebase: {
      apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
      authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
    },
  };
};

export { fileConfigProvider, cloudEnvConfigProvider };
