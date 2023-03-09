import { useMutation, useQueryClient } from "react-query";

import { useUser } from "core/AuthContext";
import { NotificationService } from "core/domain/notificationSetting/notificationSettingService";
import { EditNotificationBody, NotificationSetting, SaveNotificationUsageBody } from "core/request/DaspireClient";
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

export const useCreateNotificationSetting = () => {
  const service = useNotificationSettingApiService();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationUsage: SaveNotificationUsageBody) => service.createUsage(notificationUsage),
    onSuccess(data) {
      queryClient.setQueryData(notificationSettingKeys.get(), (setting: any) => {
        const { usageList, syncFail, syncSuccess }: NotificationSetting = setting.data;
        return { data: { usageList: [data.data, ...usageList], syncFail, syncSuccess } };
      });
    },
  });
};

export const useUpdateNotificationSetting = () => {
  const service = useNotificationSettingApiService();

  return useMutation({
    mutationFn: (editNotificationBody: EditNotificationBody) => service.edit(editNotificationBody),
    onSuccess(data, variables) {
      console.log("data", data);
      console.log("variables", variables);
    },
  });
};

export const useDeleteNotificationSetting = () => {
  const service = useNotificationSettingApiService();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationSettingId: string) => service.delete(notificationSettingId),
    onSuccess(_, variables) {
      queryClient.setQueryData(notificationSettingKeys.get(), (setting: any) => {
        const { usageList, syncFail, syncSuccess }: NotificationSetting = setting.data;
        return {
          data: {
            usageList: usageList.filter((usageItem) => usageItem.id !== variables),
            syncFail,
            syncSuccess,
          },
        };
      });
    },
  });
};

export const useAsyncActions = (): {
  onCreateNotificationSetting: (notificationUsage: SaveNotificationUsageBody) => Promise<any>;
  onUpdateNotificationSetting: (editNotificationBody: EditNotificationBody) => Promise<any>;
  onDeleteNotificationSetting: (notificationSettingId: string) => Promise<any>;
} => {
  const { mutateAsync: createNotificationSetting } = useCreateNotificationSetting();
  const { mutateAsync: updateNotificationSetting } = useUpdateNotificationSetting();
  const { mutateAsync: deleteNotificationSetting } = useDeleteNotificationSetting();

  const onCreateNotificationSetting = async (notificationUsage: SaveNotificationUsageBody) => {
    return await createNotificationSetting(notificationUsage);
  };

  const onUpdateNotificationSetting = async (editNotificationBody: EditNotificationBody) => {
    return await updateNotificationSetting(editNotificationBody);
  };

  const onDeleteNotificationSetting = async (notificationSettingId: string) => {
    return await deleteNotificationSetting(notificationSettingId);
  };

  return {
    onCreateNotificationSetting,
    onUpdateNotificationSetting,
    onDeleteNotificationSetting,
  };
};
