/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.commons.temporal.scheduling.ConnectionNotificationWorkflow;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.notification.NotificationClient;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;
import io.airbyte.workers.temporal.scheduling.activities.NotifySchemaChangeActivity;
import java.io.IOException;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ConnectionNotificationWorkflowImpl implements ConnectionNotificationWorkflow {

  @TemporalActivityStub(activityOptionsBeanName = "shortActivityOptions")
  private NotifySchemaChangeActivity notifySchemaChangeActivity;

  @Override
  public boolean sendSchemaChangeNotification(UUID connectionId, boolean isBreaking) throws IOException, InterruptedException {
    log.info("inside sending schema change notification");
    Notification notification = new Notification().withNotificationType(NotificationType.SLACK);
    NotificationClient notificationClient = NotificationClient.createNotificationClient(notification);
    log.info("notification client is: " + notificationClient);
    return notifySchemaChangeActivity.notifySchemaChange(notificationClient, connectionId, isBreaking);
  }

}
