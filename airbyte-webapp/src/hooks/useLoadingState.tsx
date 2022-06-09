import { useState } from "react";
import { useIntl } from "react-intl";

import { useNotificationService } from "./services/Notification";

const useLoadingState = (): {
  isLoading: boolean;
  startAction: ({ action, feedbackAction }: { action: () => void; feedbackAction?: () => void }) => Promise<void>;
  showFeedback: boolean;
} => {
  const { formatMessage } = useIntl();
  const { registerNotification } = useNotificationService();
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  const errorNotificationId = "error.somethingWentWrong";
  const errorNotification = (message: string) => ({
    isError: true,
    title: formatMessage({ id: `notifications.${errorNotificationId}` }),
    text: message,
    id: errorNotificationId,
  });

  const startAction = async ({ action, feedbackAction }: { action: () => void; feedbackAction?: () => void }) => {
    try {
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
    } catch (error) {
      const message = error?.message || formatMessage({ id: "notifications.error.noMessage" });

      setIsLoading(false);
      registerNotification(errorNotification(message));
    }
  };

  return { isLoading, showFeedback, startAction };
};

export default useLoadingState;
