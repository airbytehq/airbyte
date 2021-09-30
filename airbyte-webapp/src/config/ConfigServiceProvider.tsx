import React, { useContext, useMemo } from "react";
import { useAsync } from "react-use";

import { LoadingPage } from "components";

import { Config, ValueProvider } from "./types";
import { applyProviders } from "./configProviders";

type ConfigContext<T extends Config = Config> = {
  config: T;
};

const configContext = React.createContext<ConfigContext | null>(null);

export function useConfig<T extends Config>(): T {
  const configService = useContext(configContext);

  if (!configService) {
    throw new Error("useConfig must be used within a ConfigProvider");
  }

  return useMemo(() => (configService.config as unknown) as T, [
    configService.config,
  ]);
}

const ConfigServiceInner: React.FC<{
  defaultConfig: Config;
  providers: ValueProvider<Config>;
}> = ({ children, defaultConfig, providers }) => {
  const { loading, value } = useAsync(
    async () => applyProviders(defaultConfig, providers),
    [providers]
  );
  const config: ConfigContext | null = useMemo(
    () => (value ? { config: value } : null),
    [value]
  );
  return (
    <configContext.Provider value={config}>
      {loading ? <LoadingPage /> : children}
    </configContext.Provider>
  );
};

export const ConfigServiceProvider: React.FC<{
  defaultConfig: Config;
  providers: ValueProvider<Config>;
}> = React.memo(ConfigServiceInner);
