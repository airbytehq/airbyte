import { useMutation } from "react-query";

import { useUser } from "core/AuthContext";
import { NotificationService } from "core/domain/notificationSetting/notificationSettingService";
import { EditNotificationBody, SaveNotificationUsageBody } from "core/request/DaspireClient";
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

export const useSaveNotificationSetting = () => {
  const service = useNotificationSettingApiService();

  return useMutation((notificationUsage: SaveNotificationUsageBody) => service.saveUsage(notificationUsage));
};

export const useUpdateNotificationSetting = () => {
  const service = useNotificationSettingApiService();

  return useMutation((editNotificationBody: EditNotificationBody) => service.edit(editNotificationBody));
};

export const useDeleteNotificationSetting = () => {
  const service = useNotificationSettingApiService();

  return useMutation((notificationSettingId: string) => service.delete(notificationSettingId));
};

export const useAsyncActions = (): {
  onSaveNotificationSetting: (notificationUsage: SaveNotificationUsageBody) => Promise<any>;
  onUpdateNotificationSetting: (editNotificationBody: EditNotificationBody) => Promise<any>;
  onDeleteNotificationSetting: (notificationSettingId: string) => Promise<any>;
} => {
  const { mutateAsync: saveNotificationSetting } = useSaveNotificationSetting();
  const { mutateAsync: updateNotificationSetting } = useUpdateNotificationSetting();
  const { mutateAsync: deleteNotificationSetting } = useDeleteNotificationSetting();

  const onSaveNotificationSetting = async (notificationUsage: SaveNotificationUsageBody) => {
    return await saveNotificationSetting(notificationUsage);
  };

  const onUpdateNotificationSetting = async (editNotificationBody: EditNotificationBody) => {
    return await updateNotificationSetting(editNotificationBody);
  };

  const onDeleteNotificationSetting = async (notificationSettingId: string) => {
    return await deleteNotificationSetting(notificationSettingId);
  };

  return {
    onSaveNotificationSetting,
    onUpdateNotificationSetting,
    onDeleteNotificationSetting,
  };
};
