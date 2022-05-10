import { defaultConfig as coreDefaultConfig, useConfig as useCoreConfig, Config } from "config";
import { FeatureItem } from "hooks/services/Feature";

import { CloudConfig, CloudConfigExtension } from "./types";

export function useConfig(): CloudConfig {
  return useCoreConfig<CloudConfig>();
}

const features = [
  {
    id: FeatureItem.AllowOAuthConnector,
  },
];

const coreDefaultConfigOverrites: Partial<Config> = {
  features,
};

const cloudConfigExtensionDefault: CloudConfigExtension = {
  cloudApiUrl: "",
  firebase: {
    apiKey: "",
    authDomain: "",
    authEmulatorHost: "",
  },
  fullstory: {
    orgId: "",
    enabled: true,
  },
  intercom: {
    appId: "",
  },
};

export const defaultConfig: CloudConfig = Object.assign(
  {},
  coreDefaultConfig,
  coreDefaultConfigOverrites,
  cloudConfigExtensionDefault
);

export * from "./configProviders";
export * from "./types";
