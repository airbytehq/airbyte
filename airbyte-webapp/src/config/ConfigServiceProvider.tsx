import React, { useContext, useMemo } from "react";
import { useAsync } from "react-use";

import { LoadingPage } from "components";

import { applyProviders } from "./configProviders";
import { AirbyteWebappConfig, ValueProvider } from "./types";

export interface ConfigContextData<T extends AirbyteWebappConfig = AirbyteWebappConfig> {
  config: T;
}

export const ConfigContext = React.createContext<ConfigContextData | null>(null);

export function useConfig<T extends AirbyteWebappConfig>(): T {
  const configService = useContext(ConfigContext);

  if (configService === null) {
    throw new Error("useConfig must be used within a ConfigProvider");
  }

  return useMemo(() => configService.config as unknown as T, [configService.config]);
}

const ConfigServiceInner: React.FC<
  React.PropsWithChildren<{
    defaultConfig: AirbyteWebappConfig;
    providers?: ValueProvider<AirbyteWebappConfig>;
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
