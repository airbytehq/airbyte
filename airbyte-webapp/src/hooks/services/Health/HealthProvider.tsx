import React, { createContext, useContext, useState } from "react";

import { HealthCheckRead } from "core/request/AirbyteClient";

export interface HealthProviderValue {
  healthData: HealthCheckRead;
  setHealthData: React.Dispatch<React.SetStateAction<HealthCheckRead>>;
}

const HealthContext = createContext<HealthProviderValue | null>(null);

export const HealthProvider: React.FC = ({ children }) => {
  const [healthData, setHealthData] = useState<HealthCheckRead>({ available: false });

  return <HealthContext.Provider value={{ healthData, setHealthData }}>{children}</HealthContext.Provider>;
};

export const useHealth = (): HealthProviderValue => {
  const healthContext = useContext(HealthContext);

  if (!healthContext) {
    throw new Error("healthContext must be used within a");
  }

  return healthContext;
};
