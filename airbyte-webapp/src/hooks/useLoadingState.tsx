import { useState } from "react";

const useLoadingState = (): {
  isLoading: boolean;
  startAction: ({
    action,
    feedbackAction,
  }: {
    action: () => void;
    feedbackAction?: () => void;
  }) => Promise<void>;
  showFeedback: boolean;
} => {
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  const startAction = async ({
    action,
    feedbackAction,
  }: {
    action: () => void;
    feedbackAction?: () => void;
  }) => {
    setIsLoading(true);
    setShowFeedback(false);

    await action();

    setIsLoading(false);
    setShowFeedback(true);

    setTimeout(() => {
      setShowFeedback(false);
      if (feedbackAction) {
        feedbackAction();
      }
    }, 2000);
  };

  return { isLoading, showFeedback, startAction };
};

export default useLoadingState;
