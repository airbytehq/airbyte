import React from "react";

import {
  AirbyteWebappConfig,
  ConfigServiceProvider,
  ValueProvider,
  envConfigProvider,
  windowConfigProvider,
} from "config";

import { cloudEnvConfigProvider, defaultConfig, cloudWindowConfigProvider } from "./config";

const configProviders: ValueProvider<AirbyteWebappConfig> = [
  cloudEnvConfigProvider,
  cloudWindowConfigProvider,
  envConfigProvider,
  windowConfigProvider,
];

/**
 * This Provider is responsible for injecting config in context and loading
 * all required subconfigs if necessary
 */
const ConfigProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <ConfigServiceProvider defaultConfig={defaultConfig} providers={configProviders}>
    {children}
  </ConfigServiceProvider>
);

export { ConfigProvider };
