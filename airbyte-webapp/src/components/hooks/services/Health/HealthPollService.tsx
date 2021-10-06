import { useEffect, useState } from "react";
import { useIntl } from "react-intl";

import { useNotificationService } from "components/hooks/services/Notification/NotificationService";
import { HealthService } from "core/health/HealthService";

const HEALTH_NOTIFICATION_ID = "health.error";
const HEALTHCHECK_MAX_COUNT = 3;

function useApiHealthPoll(
  pollPeriod: number,
  healthService: HealthService
): void {
  const [count, setCount] = useState(0);
  const { formatMessage } = useIntl();
  const {
    registerNotification,
    unregisterNotificationById,
  } = useNotificationService();

  useEffect(() => {
    const errorNotification = {
      id: HEALTH_NOTIFICATION_ID,
      title: formatMessage({ id: "notifications.error.health" }),
      isError: true,
    };

    const interval = setInterval(async () => {
      try {
        await healthService.health();
        if (count >= HEALTHCHECK_MAX_COUNT) {
          unregisterNotificationById(HEALTH_NOTIFICATION_ID);
        }
        setCount(0);
      } catch (e) {
        if (count < HEALTHCHECK_MAX_COUNT) {
          setCount((count) => ++count);
        } else {
          registerNotification(errorNotification);
        }
      }
    }, pollPeriod);

    return () => clearInterval(interval);
  }, [
    count,
    pollPeriod,
    formatMessage,
    unregisterNotificationById,
    registerNotification,
  ]);
}

export { useApiHealthPoll };
