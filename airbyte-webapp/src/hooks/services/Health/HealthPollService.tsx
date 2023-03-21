import { useEffect, useState } from "react";
import { useIntl } from "react-intl";

import { useConfig } from "config";
import { HealthService } from "core/health/HealthService";
import { useGetService } from "core/servicesProvider";
import { useNotificationService } from "hooks/services/Notification/NotificationService";

import { useAppNotification } from "../AppNotification";
import { useHealth } from "./HealthProvider";

const HEALTH_NOTIFICATION_ID = "health.error";
const HEALTHCHECK_MAX_COUNT = 3;

function useApiHealthPoll(): void {
  const [count, setCount] = useState(0);
  const { formatMessage } = useIntl();
  const { healthCheckInterval } = useConfig();
  const healthService = useGetService<HealthService>("HealthService");
  const { registerNotification, unregisterNotificationById } = useNotificationService();
  const { setHealthData } = useHealth();
  const { setNotification } = useAppNotification();

  useEffect(() => {
    const errorNotification = {
      id: HEALTH_NOTIFICATION_ID,
      title: formatMessage({ id: "notifications.error.health" }),
      isError: true,
    };

    const interval = setInterval(async () => {
      try {
        const data = await healthService.health();
        if (data) {
          setHealthData(data);
        }

        const { syncFail, syncSuccess } = data;

        if (syncFail) {
          setNotification({ message: syncFail[0], type: "error" });
        }
        if (syncSuccess) {
          setNotification({ message: syncSuccess[0], type: "info" });
        }

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
    }, healthCheckInterval);

    return () => clearInterval(interval);
  }, [count, healthCheckInterval, formatMessage, unregisterNotificationById, registerNotification, healthService]);
}

export { useApiHealthPoll };
