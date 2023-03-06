import { useUser } from "core/AuthContext";
import { NotificationService } from "core/domain/notificationSetting/notificationSettingService";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { SCOPE_USER } from "../Scope";
import { useInitService } from "../useInitService";

export const notificationSettingKeys = {
  all: [SCOPE_USER, "notificationSetting"] as const,
  get: () => [...notificationSettingKeys.all, "get"] as const,
};

function useNotificationSettingApiService() {
  const { removeUser } = useUser();
  const middlewares = useDefaultRequestMiddlewares();

  return useInitService(
    () => new NotificationService(process.env.REACT_APP_API_URL as string, middlewares, removeUser),
    [process.env.REACT_APP_API_URL as string, middlewares, removeUser]
  );
}

export const useNotificationSetting = () => {
  const service = useNotificationSettingApiService();
  return useSuspenseQuery(notificationSettingKeys.get(), () => service.get()).data;
};
