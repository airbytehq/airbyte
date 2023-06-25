import { useMutation, useQueryClient } from "react-query";

import { useUser } from "core/AuthContext";
import { NotificationService } from "core/domain/notificationSetting/notificationSettingService";
import {
  IgnoreNotificationBody,
  NotificationItem,
  NotificationSetting,
  SaveNotificationUsageBody,
} from "core/request/DaspireClient";
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
        const { usageList, syncFail, syncSuccess, paymentFail }: NotificationSetting = setting.data;
        return { data: { usageList: [data.data, ...usageList], syncFail, syncSuccess, paymentFail } };
      });
    },
  });
};

export const useUpdateNotificationSetting = () => {
  const service = useNotificationSettingApiService();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: NotificationItem) => service.edit(data),
    onSuccess(data) {
      const response = data.data;
      queryClient.setQueryData(notificationSettingKeys.get(), (setting: any) => {
        const { usageList, syncFail, syncSuccess, paymentFail }: NotificationSetting = setting.data;
        let mySyncFail = { ...syncFail };
        let mySyncSuccess = { ...syncSuccess };
        let myPaymentFail = { ...paymentFail };
        if (response.type === "SYNC_FAIL") {
          mySyncFail = response;
        } else if (response.type === "SYNC_SUCCESS") {
          mySyncSuccess = response;
        } else if (response.type === "PAYMENT_FAIL") {
          myPaymentFail = response;
        } else {
          return { data: { usageList, syncFail, syncSuccess, paymentFail } };
        }
        return {
          data: {
            usageList,
            syncFail: mySyncFail,
            syncSuccess: mySyncSuccess,
            paymentFail: myPaymentFail,
          },
        };
      });
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
        const { usageList, syncFail, syncSuccess, paymentFail }: NotificationSetting = setting.data;
        return {
          data: {
            usageList: usageList.filter((usageItem) => usageItem.id !== variables),
            syncFail,
            syncSuccess,
            paymentFail,
          },
        };
      });
    },
  });
};

export const useIgnoreNotifications = () => {
  const service = useNotificationSettingApiService();

  return useMutation((ignoreNotificationBody: IgnoreNotificationBody) => service.ignore(ignoreNotificationBody));
};

export const useAsyncActions = (): {
  onCreateNotificationSetting: (notificationUsage: SaveNotificationUsageBody) => Promise<any>;
  onUpdateNotificationSetting: (data: NotificationItem) => Promise<any>;
  onDeleteNotificationSetting: (notificationSettingId: string) => Promise<any>;
  onIgnoreNotifications: (ignoreNotificationBody: IgnoreNotificationBody) => Promise<any>;
} => {
  const { mutateAsync: createNotificationSetting } = useCreateNotificationSetting();
  const { mutateAsync: updateNotificationSetting } = useUpdateNotificationSetting();
  const { mutateAsync: deleteNotificationSetting } = useDeleteNotificationSetting();
  const { mutateAsync: ignoreNotifications } = useIgnoreNotifications();

  const onCreateNotificationSetting = async (notificationUsage: SaveNotificationUsageBody) => {
    return await createNotificationSetting(notificationUsage);
  };

  const onUpdateNotificationSetting = async (data: NotificationItem) => {
    return await updateNotificationSetting(data);
  };

  const onDeleteNotificationSetting = async (notificationSettingId: string) => {
    return await deleteNotificationSetting(notificationSettingId);
  };

  const onIgnoreNotifications = async (ignoreNotificationBody: IgnoreNotificationBody) => {
    return await ignoreNotifications(ignoreNotificationBody);
  };

  return {
    onCreateNotificationSetting,
    onUpdateNotificationSetting,
    onDeleteNotificationSetting,
    onIgnoreNotifications,
  };
};
