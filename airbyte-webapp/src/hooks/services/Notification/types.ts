export type Notification = {
  id: string | number;
  title: string;
  text?: string;
  isError?: boolean;
  nonClosable?: boolean;
  onClose?: () => void;
};

export type NotificationServiceApi = {
  addNotification: (notification: Notification) => void;
  deleteNotificationById: (notificationId: string | number) => void;
  clearAll: () => void;
};

export type NotificationServiceState = {
  notifications: Notification[];
};
