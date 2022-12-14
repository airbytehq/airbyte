import type { Experiments } from "./experiments";

import { createContext, useContext, useMemo } from "react";
import { useObservable } from "react-use";
import { EMPTY, Observable } from "rxjs";

const experimentContext = createContext<ExperimentService | null>(null);

/**
 * An ExperimentService must be able to give us a value for a given key of an experiment
 * as well as update us about changes in the experiment.
 */
export interface ExperimentService {
  getExperiment<K extends keyof Experiments>(key: K, defaultValue: Experiments[K]): Experiments[K];
  getExperimentChanges$<K extends keyof Experiments>(key: K): Observable<Experiments[K]>;
}

export function useExperiment<K extends keyof Experiments>(key: K, defaultValue: Experiments[K]): Experiments[K] {
  const envOverwrite = useMemo(() => {
    if (process.env.NODE_ENV !== "development" || !process.env[`REACT_APP_EXPERIMENT_${key}`]) {
      return null;
    }

    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    return JSON.parse(process.env[`REACT_APP_EXPERIMENT_${key}`]!);
  }, [key]);

  const experimentService = useContext(experimentContext);
  // Get the observable for the changes of the experiment or an empty (never emitting) observable in case the
  // experiment service doesn't exist (e.g. we're running in OSS or it failed to initialize)

  const onChanges$ = useMemo(
    () => (envOverwrite ? EMPTY : experimentService?.getExperimentChanges$(key) ?? EMPTY),
    [envOverwrite, experimentService, key]
  );
  // Listen to changes on that observable and use the current value (if the service exist) or the defaultValue otherwise
  // as the starting value.

  return useObservable(onChanges$, envOverwrite ?? experimentService?.getExperiment(key, defaultValue) ?? defaultValue);
}

export const ExperimentProvider = experimentContext.Provider;
