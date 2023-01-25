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
