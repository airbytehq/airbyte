import merge from "lodash.merge";
import { ConfigProvider, DeepPartial, ValueProvider } from "./types";
import { isDefined } from "utils/common";

const windowConfigProvider: ConfigProvider = async () => {
  return {
    fullstory: { devMode: window.FULLSTORY === "disabled" },
    segment: {
      enabled: isDefined(window.TRACKING_STRATEGY)
        ? window.TRACKING_STRATEGY === "segment"
        : undefined,
    },
    apiUrl: window.API_URL,
    version: window.AIRBYTE_VERSION,
    isDemo: window.IS_DEMO === "true",
    // cloud only start
    firebase: {
      apiKey: window.FIREBASE_API_KEY,
      authDomain: window.FIREBASE_AUTH_DOMAIN,
    },
    cloudApiUrl: window.CLOUD_API_URL,
    cloud: window.CLOUD === "true",
    // cloud only end
  };
};

const envConfigProvider: ConfigProvider = async () => {
  return {
    apiUrl: process.env.REACT_APP_API_URL,
    segment: {
      token: process.env.REACT_APP_SEGMENT_TOKEN,
    },
    fullstory: {
      orgId: process.env.REACT_APP_FULL_STORY_ORG,
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

export { windowConfigProvider, envConfigProvider, applyProviders };
