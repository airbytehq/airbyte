import {
  defaultConfig as coreDefaultConfig,
  useConfig as useCoreConfig,
  Config,
} from "config";
import { CloudConfig, CloudConfigExtension } from "./types";
import { FeatureItem } from "hooks/services/Feature";

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
