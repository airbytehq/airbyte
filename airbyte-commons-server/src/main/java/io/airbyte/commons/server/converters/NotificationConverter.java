/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

import io.airbyte.commons.enums.Enums;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class NotificationConverter {

  public static List<io.airbyte.config.Notification> toConfigList(final List<io.airbyte.api.model.generated.Notification> notifications) {
    if (notifications == null) {
      return Collections.emptyList();
    }
    return notifications.stream().map(NotificationConverter::toConfig).collect(Collectors.toList());
  }

  public static io.airbyte.config.Notification toConfig(final io.airbyte.api.model.generated.Notification notification) {
    return new io.airbyte.config.Notification()
        .withNotificationType(Enums.convertTo(notification.getNotificationType(), io.airbyte.config.Notification.NotificationType.class))
        .withSendOnSuccess(notification.getSendOnSuccess())
        .withSendOnFailure(notification.getSendOnFailure())
        .withSlackConfiguration(toConfig(notification.getSlackConfiguration()));
  }

  private static io.airbyte.config.SlackNotificationConfiguration toConfig(final io.airbyte.api.model.generated.SlackNotificationConfiguration notification) {
    return new io.airbyte.config.SlackNotificationConfiguration()
        .withWebhook(notification.getWebhook());
  }

  public static List<io.airbyte.api.model.generated.Notification> toApiList(final List<io.airbyte.config.Notification> notifications) {
    return notifications.stream().map(NotificationConverter::toApi).collect(Collectors.toList());
  }

  public static io.airbyte.api.model.generated.Notification toApi(final io.airbyte.config.Notification notification) {
    return new io.airbyte.api.model.generated.Notification()
        .notificationType(Enums.convertTo(notification.getNotificationType(), io.airbyte.api.model.generated.NotificationType.class))
        .sendOnSuccess(notification.getSendOnSuccess())
        .sendOnFailure(notification.getSendOnFailure())
        .slackConfiguration(toApi(notification.getSlackConfiguration()));
  }

  private static io.airbyte.api.model.generated.SlackNotificationConfiguration toApi(final io.airbyte.config.SlackNotificationConfiguration notification) {
    return new io.airbyte.api.model.generated.SlackNotificationConfiguration()
        .webhook(notification.getWebhook());
  }

}
