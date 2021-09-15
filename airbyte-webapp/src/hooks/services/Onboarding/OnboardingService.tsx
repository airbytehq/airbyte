import React, { useContext, useMemo } from "react";
import { useLocalStorage } from "react-use";
import useWorkspace from "hooks/services/useWorkspace";

type Context = {
  feedbackPassed?: boolean;
  passFeedback: () => void;
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

  const ctx = useMemo<Context>(
    () => ({
      feedbackPassed,
      passFeedback: () => setFeedbackPassed(true),
    }),
    [feedbackPassed]
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
