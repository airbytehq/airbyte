import React, { useContext, useMemo } from "react";
import { useAsync } from "react-use";

import { Config, ValueProvider } from "./types";
import { LoadingPage } from "../components";
import { applyProviders } from "./configProviders";

type ConfigContext<T extends Config = Config> = {
  config: T;
};

const configContext = React.createContext<ConfigContext | null>(null);

export function useConfig<T extends Config>(): T {
  const config = useContext(configContext);

  if (!config) {
    throw new Error("useConfig must be used within a ConfigProvider");
  }

  return (config as unknown) as T;
}

export const ConfigService: React.FC<{
  providers: ValueProvider<Config>;
}> = ({ children, providers }) => {
  const { loading, value } = useAsync(() => applyProviders(providers), []);
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
