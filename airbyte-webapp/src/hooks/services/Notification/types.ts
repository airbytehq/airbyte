import React from "react";

export interface Notification {
  id: string | number;
  title: React.ReactNode;
  text?: React.ReactNode;
  isError?: boolean;
  nonClosable?: boolean;
  onClose?: () => void;
}

export interface NotificationServiceApi {
  addNotification: (notification: Notification) => void;
  deleteNotificationById: (notificationId: string | number) => void;
  clearAll: () => void;
}

export interface NotificationServiceState {
  notifications: Notification[];
}
