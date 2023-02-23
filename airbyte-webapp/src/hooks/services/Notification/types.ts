import { ToastProps } from "components/ui/Toast";

export interface Notification extends Pick<ToastProps, "type" | "onAction" | "onClose" | "actionBtnText" | "text"> {
  id: string;
  nonClosable?: boolean;
}

export interface NotificationServiceApi {
  addNotification: (notification: Notification) => void;
  deleteNotificationById: (notificationId: string | number) => void;
  clearAll: () => void;
}

export interface NotificationServiceState {
  notifications: Notification[];
}
