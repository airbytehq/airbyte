import { ConfigProvider } from "config/types";
import { CloudConfig } from "./types";

const fileConfigProvider: ConfigProvider<CloudConfig> = async () => {
  const response = await fetch("/config.json");

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
    firebase: {},
  };
};

export { fileConfigProvider, cloudEnvConfigProvider };
