import React, { createContext, useContext, useMemo, useState } from "react";

import { HealthCheckRead } from "core/request/AirbyteClient";

export interface Context {
  healthData: HealthCheckRead;
  setHealthData: React.Dispatch<React.SetStateAction<HealthCheckRead>>;
}

const HealthContext = createContext<Context | null>(null);

export const HealthProvider: React.FC = ({ children }) => {
  const [healthData, setHealthData] = useState<HealthCheckRead>({ available: false, isPaymentFailed: false });

  const ctx = useMemo<Context>(() => ({ healthData, setHealthData }), [healthData]);

  return <HealthContext.Provider value={ctx}>{children}</HealthContext.Provider>;
};

export const useHealth = (): Context => {
  const healthContext = useContext(HealthContext);
  if (!healthContext) {
    throw new Error("useHealth must be used within a HealthProvider.");
  }

  return healthContext;
};
