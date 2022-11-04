import React, { useContext, useMemo } from "react";
import { useLocalStorage } from "react-use";

import casesConfig from "config/casesConfig.json";

// import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { getAuthenticatedUser } from "../../../services/auth/AuthService";

interface Context {
  feedbackPassed?: boolean;
  passFeedback: () => void;
  visibleUseCases?: string[];
  useCaseLinks: Record<string, string>;
  skipCase: (skipId: string) => void;
}

export const OnboardingServiceContext = React.createContext<Context | null>(null);

export const OnboardingServiceProvider: React.FC = ({ children }) => {
  // const workspace = useCurrentWorkspace();
  const user = getAuthenticatedUser();
  const [feedbackPassed, setFeedbackPassed] = useLocalStorage<boolean>(`${user.workspaceId}/passFeedback`, false);
  const [skippedUseCases, setSkippedUseCases] = useLocalStorage<string[]>(`${user.workspaceId}/skippedUseCases`, []);

  const ctx = useMemo<Context>(
    () => ({
      feedbackPassed,
      passFeedback: () => setFeedbackPassed(true),
      visibleUseCases: Object.keys(casesConfig).filter((useCase) => !skippedUseCases?.includes(useCase)),
      useCaseLinks: casesConfig,
      skipCase: (skipId: string) => setSkippedUseCases([...(skippedUseCases ?? []), skipId]),
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [feedbackPassed, skippedUseCases]
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
