import React, { useContext, useMemo } from "react";
import { useLocalStorage } from "react-use";
import useWorkspace from "hooks/services/useWorkspace";
import casesConfig from "config/casesConfig.json";

type Context = {
  feedbackPassed?: boolean;
  passFeedback: () => void;
  useCases?: string[];
  skipCase: (skipId: string) => void;
};

export const OnboardingServiceContext = React.createContext<Context | null>(
  null
);

export const OnboardingServiceProvider: React.FC = ({ children }) => {
  const { workspace } = useWorkspace();
  const [feedbackPassed, setFeedbackPassed] = useLocalStorage<boolean>(
    `${workspace.workspaceId}/passFeedback`,
    false
  );
  const [useCases, setUseCases] = useLocalStorage<string[]>(
    `${workspace.workspaceId}/useCases`,
    casesConfig
  );

  const ctx = useMemo<Context>(
    () => ({
      feedbackPassed,
      passFeedback: () => setFeedbackPassed(true),
      useCases,
      skipCase: (skipId: string) =>
        setUseCases(useCases?.filter((item) => item !== skipId)),
    }),
    [feedbackPassed, useCases]
  );

  return (
    <OnboardingServiceContext.Provider value={ctx}>
      {children}
    </OnboardingServiceContext.Provider>
  );
};

export const useOnboardingService = (): Context => {
  const onboardingService = useContext(OnboardingServiceContext);
  if (!onboardingService) {
    throw new Error(
      "useOnboardingService must be used within a OnboardingServiceProvider."
    );
  }

  return onboardingService;
};
