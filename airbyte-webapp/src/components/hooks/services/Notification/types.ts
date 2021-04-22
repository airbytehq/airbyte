export type Notification = {
  id: string | number;
  title: string;
  text?: string;
  isError?: boolean;
};

export type NotificationServiceApi = {
  addNotification: (notification: Notification) => void;
  deleteNotification: (notification: Notification) => void;
  clearAll: () => void;
};

export type NotificationServiceState = {
  notifications: Notification[];
};
