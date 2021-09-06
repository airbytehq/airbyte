import merge from "lodash.merge";
import { ConfigProvider, DeepPartial, ValueProvider } from "./types";
import { isDefined } from "utils/common";

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
      enabled: isDefined(window.TRACKING_STRATEGY)
        ? window.TRACKING_STRATEGY === "segment"
        : undefined,
    },
    apiUrl: window.API_URL,
    version: window.AIRBYTE_VERSION,
    isDemo: window.IS_DEMO === "true",
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
    openreplay: {
      projectID:
        isDefined(process.env.REACT_APP_OPEN_REPLAY_PROJECT_ID) &&
        Number.isInteger(process.env.REACT_APP_OPEN_REPLAY_PROJECT_ID)
          ? Number.parseInt(process.env.REACT_APP_OPEN_REPLAY_PROJECT_ID)
          : -1,
    },
    papercups: {
      accountId: process.env.REACT_APP_PAPERCUPS_ACCOUNT_ID,
      enableStorytime: isDefined(
        process.env.REACT_APP_PAPERCUPS_DISABLE_STORYTIME
      )
        ? !process.env.REACT_APP_PAPERCUPS_DISABLE_STORYTIME
        : undefined,
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
