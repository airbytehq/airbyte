import React, { useContext } from "react";

import { AirbyteWebappConfig } from "./types";

export interface ConfigContextData {
  config: AirbyteWebappConfig;
}

export const ConfigContext = React.createContext<ConfigContextData | null>(null);

export function useConfig(): AirbyteWebappConfig {
  const configService = useContext(ConfigContext);

  if (configService === null) {
    throw new Error("useConfig must be used within a ConfigProvider");
  }

  return configService.config;
}

export const ConfigServiceProvider: React.FC<
  React.PropsWithChildren<{
    config: AirbyteWebappConfig;
  }>
> = ({ children, config }) => {
  return <ConfigContext.Provider value={{ config }}>{children}</ConfigContext.Provider>;
};
