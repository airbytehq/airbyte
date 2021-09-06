import React, { useContext, useEffect, useMemo } from "react";

import SingletonCard from "components/SingletonCard";

import {
  Notification,
  NotificationServiceApi,
  NotificationServiceState,
} from "./types";
import useTypesafeReducer from "hooks/useTypesafeReducer";
import { actions, initialState, notificationServiceReducer } from "./reducer";

const notificationServiceContext = React.createContext<NotificationServiceApi | null>(
  null
);

function NotificationService({ children }: { children: React.ReactNode }) {
  const [
    state,
    { addNotification, clearAll, deleteNotificationById },
  ] = useTypesafeReducer<NotificationServiceState, typeof actions>(
    notificationServiceReducer,
    initialState,
    actions
  );

  const notificationService: NotificationServiceApi = useMemo(
    () => ({
      addNotification,
      deleteNotificationById,
      clearAll,
    }),
    []
  );

  const firstNotification =
    state.notifications && state.notifications.length
      ? state.notifications[0]
      : null;

  return (
    <>
      <notificationServiceContext.Provider value={notificationService}>
        {children}
      </notificationServiceContext.Provider>
      {firstNotification ? (
        // Show only first notification
        <SingletonCard
          title={firstNotification.title}
          text={firstNotification.text}
          hasError={firstNotification.isError}
          onClose={
            firstNotification.nonClosable
              ? undefined
              : () => {
                  deleteNotificationById(firstNotification.id);
                  firstNotification.onClose?.();
                }
          }
        />
      ) : null}
    </>
  );
}

export const useNotificationService: (
  notification?: Notification,
  dependencies?: []
) => {
  registerNotification: (notification: Notification) => void;
  unregisterAllNotifications: () => void;
  unregisterNotificationById: (notificationId: string | number) => void;
} = (notification, dependencies) => {
  const notificationService = useContext(notificationServiceContext);
  if (!notificationService) {
    throw new Error(
      "useNotificationService must be used within a NotificationService."
    );
  }

  useEffect(() => {
    if (notification) {
      notificationService.addNotification(notification);
    }
    return () => {
      if (notification) {
        notificationService.deleteNotificationById(notification.id);
      }
    };
    // eslint-disable-next-line
  }, [notification, notificationService, ...(dependencies || [])]);

  return {
    registerNotification: notificationService.addNotification,
    unregisterNotificationById: notificationService.deleteNotificationById,
    unregisterAllNotifications: notificationService.clearAll,
  };
};

export default React.memo(NotificationService);
