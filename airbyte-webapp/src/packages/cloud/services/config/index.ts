import {
  defaultConfig as coreDefaultConfig,
  useConfig as useCoreConfig,
} from "config";
import { CloudConfig, CloudConfigExtension } from "./types";

export function useConfig(): CloudConfig {
  return useCoreConfig<CloudConfig>();
}

const cloudConfigExtensionDefault: CloudConfigExtension = {
  cloudApiUrl: "",
  firebase: {
    apiKey: "",
    authDomain: "",
  },
};

export const defaultConfig: CloudConfig = Object.assign(
  {},
  coreDefaultConfig,
  cloudConfigExtensionDefault
);

export * from "./configProviders";
export * from "./types";
