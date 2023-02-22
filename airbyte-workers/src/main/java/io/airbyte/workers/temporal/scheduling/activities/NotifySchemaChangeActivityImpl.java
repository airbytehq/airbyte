/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.notification.SlackNotificationClient;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.UUID;

@Singleton
public class NotifySchemaChangeActivityImpl implements NotifySchemaChangeActivity {

  @Override
  public boolean notifySchemaChange(UUID connectionId, boolean isBreaking, SlackNotificationConfiguration slackConfig, String url)
      throws IOException, InterruptedException {
    final Notification notification = createNotification(slackConfig);
    final SlackNotificationClient notificationClient = createNotificationClient(notification);
    return notificationClient.notifySchemaChange(connectionId, isBreaking, slackConfig, url);
  }

  Notification createNotification(SlackNotificationConfiguration slackConfig) {
    return new Notification().withNotificationType(NotificationType.SLACK).withSendOnFailure(false).withSendOnSuccess(false)
        .withSlackConfiguration(slackConfig);
  }

  SlackNotificationClient createNotificationClient(Notification notification) {
    return new SlackNotificationClient(notification);
  }

}
