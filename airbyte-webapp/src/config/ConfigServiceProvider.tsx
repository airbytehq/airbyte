import React, { useContext, useMemo } from "react";
import { useAsync } from "react-use";

import { LoadingPage } from "components";

import { applyProviders } from "./configProviders";
import { Config, ValueProvider } from "./types";

export interface ConfigContextData<T extends Config = Config> {
  config: T;
}

export const ConfigContext = React.createContext<ConfigContextData | null>(null);

export function useConfig<T extends Config>(): T {
  const configService = useContext(ConfigContext);

  if (configService === null) {
    throw new Error("useConfig must be used within a ConfigProvider");
  }

  return useMemo(() => configService.config as unknown as T, [configService.config]);
}

const ConfigServiceInner: React.FC<
  React.PropsWithChildren<{
    defaultConfig: Config;
    providers?: ValueProvider<Config>;
  }>
> = ({ children, defaultConfig, providers }) => {
  const { loading, value } = useAsync(
    async () => (providers ? applyProviders(defaultConfig, providers) : defaultConfig),
    [providers]
  );
  const config: ConfigContextData | null = useMemo(() => (value ? { config: value } : null), [value]);

  if (loading) {
    return <LoadingPage />;
  }

  return <ConfigContext.Provider value={config}>{children}</ConfigContext.Provider>;
};

export const ConfigServiceProvider = React.memo(ConfigServiceInner);
