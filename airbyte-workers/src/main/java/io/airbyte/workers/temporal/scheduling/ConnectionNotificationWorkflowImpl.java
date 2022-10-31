/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.commons.temporal.scheduling.ConnectionNotificationWorkflow;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.notification.NotificationClient;

public class ConnectionNotificationWorkflowImpl implements ConnectionNotificationWorkflow {

  @Override
  public void sendSchemaChangeNotification() {
    Notification notification = new Notification().withNotificationType(NotificationType.SLACK);
    NotificationClient notificationClient = NotificationClient.createNotificationClient(notification);
  }

}
