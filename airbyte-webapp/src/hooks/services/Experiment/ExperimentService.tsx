import type { Experiments } from "./experiments";

import { createContext, useContext, useMemo } from "react";
import { useObservable } from "react-use";
import { EMPTY, Observable } from "rxjs";

const experimentContext = createContext<ExperimentService | null>(null);

export interface ExperimentService {
  getExperiment<K extends keyof Experiments>(key: K, defaultValue: Experiments[K]): Experiments[K];
  getExperimentChanges$<K extends keyof Experiments>(key: K): Observable<Experiments[K]>;
}

export function useExperiment<K extends keyof Experiments>(key: K, defaultValue: Experiments[K]): Experiments[K] {
  const experimentService = useContext(experimentContext);
  const onChanges$ = useMemo(() => experimentService?.getExperimentChanges$(key) ?? EMPTY, [experimentService, key]);
  const value = useObservable(onChanges$, experimentService?.getExperiment(key, defaultValue) ?? defaultValue);
  console.log(`useExperiment(${key}): ${JSON.stringify(value)}`);
  return value;
}

export const ExperimentProvider = experimentContext.Provider;
