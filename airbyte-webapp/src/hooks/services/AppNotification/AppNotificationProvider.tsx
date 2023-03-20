import React, { createContext, useContext, useState } from "react";

export interface AppNotification {
  message: string;
  type: "info" | "error";
}

export interface AppNotificationProviderValue {
  notification: AppNotification;
  setNotification: React.Dispatch<React.SetStateAction<AppNotification>>;
}

const AppNotificationContext = createContext<AppNotificationProviderValue | null>(null);

export const appNotificationInitialState: AppNotification = { message: "", type: "info" };

export const AppNotificationProvider: React.FC = ({ children }) => {
  const [notification, setNotification] = useState<AppNotification>(appNotificationInitialState);

  return (
    <AppNotificationContext.Provider value={{ notification, setNotification }}>
      {children}
    </AppNotificationContext.Provider>
  );
};

export const useAppNotification = (): AppNotificationProviderValue => {
  const appNotificationContext = useContext(AppNotificationContext);

  if (!appNotificationContext) {
    throw new Error("AppNotificationContext must be used within a");
  }

  return appNotificationContext;
};
