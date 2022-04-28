import { ActionType, createAction, createReducer } from "typesafe-actions";

import { Notification, NotificationServiceState } from "./types";

export const actions = {
  addNotification: createAction("ADD_NOTIFICATION")<Notification>(),
  deleteNotificationById: createAction("DELETE_NOTIFICATION_BY_ID")<string | number>(),
  clearAll: createAction("CLEAR_ALL")(),
};

type Actions = ActionType<typeof actions>;

function removeNotification(notifications: Notification[], notificationId: string | number): Notification[] {
  return notifications.filter((n) => n.id !== notificationId);
}

function findNotification(notifications: Notification[], notification: Notification): Notification | undefined {
  return notifications.find((n) => n.id === notification.id);
}

export const initialState: NotificationServiceState = {
  notifications: [],
};

export const notificationServiceReducer = createReducer<NotificationServiceState, Actions>(initialState)
  .handleAction(actions.addNotification, (state, action): NotificationServiceState => {
    if (findNotification(state.notifications, action.payload)) {
      return state;
    }

    const notifications = [action.payload].concat(state.notifications);
    return {
      ...state,
      notifications,
    };
  })
  .handleAction(actions.deleteNotificationById, (state, action): NotificationServiceState => {
    const notifications = removeNotification(state.notifications, action.payload);

    return {
      ...state,
      notifications,
    };
  })
  .handleAction(
    actions.clearAll,
    (state, _): NotificationServiceState => ({
      ...state,
      notifications: [],
    })
  );
