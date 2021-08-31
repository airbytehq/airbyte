import merge from "lodash.merge";
import { ConfigProvider, DeepPartial, ValueProvider } from "./types";

const fileConfigProvider: ConfigProvider = async () => {
  const response = await fetch("/config.json");

  if (response.ok) {
    try {
      const config = await response.json();

      return config;
    } catch (e) {
      console.error("error occured while parsing the json config");
    }
  }

  return {};
};

const windowConfigProvider: ConfigProvider = async () => {
  return {
    papercups: {
      enableStorytime: window.PAPERCUPS_STORYTIME !== "disabled",
    },
    openreplay: {
      projectID: window.OPENREPLAY === "disabled" ? -1 : undefined,
      revID: window.AIRBYTE_VERSION,
    },
    fullstory: { devMode: window.FULLSTORY === "disabled" },
    segment: {
      enabled: window.TRACKING_STRATEGY === "segment",
    },
    apiUrl: window.API_URL,
    version: window.AIRBYTE_VERSION,
    isDemo: window.IS_DEMO === "true",
  };
};

const envConfigProvider: ConfigProvider = async () => {
  return {
    apiUrl: process.env.REACT_APP_API_URL,
    fullstory: {
      orgId: process.env.REACT_APP_FULL_STORY_ORG,
    },
    papercups: {
      accountId: process.env.REACT_APP_PAPERCUPS_ACCOUNT_ID,
      enableStorytime: !process.env.REACT_APP_PAPERCUPS_DISABLE_STORYTIME,
    },
  };
};

async function applyProviders<T>(
  defaultValue: T,
  providers: ValueProvider<T>
): Promise<T> {
  let value: DeepPartial<T> = {};

  for (const provider of providers) {
    const partialConfig = await provider();

    value = merge(value, partialConfig);
  }

  return merge(defaultValue, value);
}

export {
  fileConfigProvider,
  windowConfigProvider,
  envConfigProvider,
  applyProviders,
};
