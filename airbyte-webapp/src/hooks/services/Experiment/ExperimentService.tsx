import type { Experiments } from "./experiments";

import { createContext, useContext } from "react";

const experimentContext = createContext<ExperimentService | null>(null);

export interface ExperimentService {
  getExperiment<K extends keyof Experiments>(key: K, defaultValue: Experiments[K]): Experiments[K];
}

export function useExperiment<K extends keyof Experiments>(key: K, defaultValue: Experiments[K]): Experiments[K] {
  const experimentService = useContext(experimentContext);
  if (!experimentService) {
    // If we're not having an experiment service provided, we'll always return the default value.
    // This is an expected state runnning in OSS or if the experimentation service failed to initialize.
    return defaultValue;
  }
  return experimentService.getExperiment(key, defaultValue);
}

export const ExperimentProvider = experimentContext.Provider;
