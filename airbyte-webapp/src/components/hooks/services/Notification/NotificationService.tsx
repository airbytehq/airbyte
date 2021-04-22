import React, { useContext, useEffect } from "react";

import {
  NotificationServiceApi,
  Notification,
  NotificationServiceState,
} from "./types";
import useTypesafeReducer from "../useTypesafeReducer";
import { actions, initialState, notificationServiceReducer } from "./reducer";
import SingletonCard from "components/SingletonCard";

const notificationServiceContext = React.createContext<NotificationServiceApi | null>(
  null
);

function NotificationService({ children }: { children: React.ReactNode }) {
  const [
    state,
    { addNotification, deleteNotification, clearAll },
  ] = useTypesafeReducer<NotificationServiceState, typeof actions>(
    notificationServiceReducer,
    initialState,
    actions
  );

  const notificationService: NotificationServiceApi = {
    addNotification,
    deleteNotification,
    clearAll,
  };

  return (
    <>
      <notificationServiceContext.Provider value={notificationService}>
        {children}
      </notificationServiceContext.Provider>
      {state.notifications && state.notifications.length ? (
        // Show only first notification
        <SingletonCard
          title={state.notifications[0].title}
          text={state.notifications[0].text}
          hasError={state.notifications[0].isError}
          onClose={state.notifications[0].onClose}
        />
      ) : null}
    </>
  );
}

export const useNotificationService = (
  notification?: Notification,
  dependencies?: []
) => {
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
      if (notification) notificationService.deleteNotification(notification);
    };
    // eslint-disable-next-line
  }, [notification, notificationService, ...(dependencies || [])]);

  return {
    registerNotification: notificationService.addNotification,
    unregisterNotification: notificationService.deleteNotification,
    unregisterAllNotifications: notificationService.clearAll,
  };
};

export default React.memo(NotificationService);
