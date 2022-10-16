import React, { useContext, useMemo } from "react";
import { useLocalStorage } from "react-use";

import casesConfig from "config/casesConfig.json";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

interface Context {
  visibleUseCases?: string[];
  useCaseLinks: Record<string, string>;
  skipCase: (skipId: string) => void;
}

export const OnboardingServiceContext = React.createContext<Context | null>(null);

export const OnboardingServiceProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const workspace = useCurrentWorkspace();
  const [skippedUseCases, setSkippedUseCases] = useLocalStorage<string[]>(
    `${workspace.workspaceId}/skippedUseCases`,
    []
  );

  const ctx = useMemo<Context>(
    () => ({
      visibleUseCases: Object.keys(casesConfig).filter((useCase) => !skippedUseCases?.includes(useCase)),
      useCaseLinks: casesConfig,
      skipCase: (skipId: string) => setSkippedUseCases([...(skippedUseCases ?? []), skipId]),
    }),
    [setSkippedUseCases, skippedUseCases]
  );

  return <OnboardingServiceContext.Provider value={ctx}>{children}</OnboardingServiceContext.Provider>;
};

export const useOnboardingService = (): Context => {
  const onboardingService = useContext(OnboardingServiceContext);
  if (!onboardingService) {
    throw new Error("useOnboardingService must be used within a OnboardingServiceProvider.");
  }

  return onboardingService;
};
