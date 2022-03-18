/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.commons.enums.Enums;
import java.util.List;
import java.util.stream.Collectors;

public class NotificationConverter {

  public static List<io.airbyte.config.NotificationLegacy> toConfigList(final List<io.airbyte.api.model.NotificationLegacy> notifications) {
    return notifications.stream().map(NotificationConverter::toConfig).collect(Collectors.toList());
  }

  public static io.airbyte.config.NotificationLegacy toConfig(final io.airbyte.api.model.NotificationLegacy notification) {
    return new io.airbyte.config.NotificationLegacy()
        .withNotificationType(Enums.convertTo(notification.getNotificationType(), io.airbyte.config.Notification.NotificationType.class))
        .withSendOnSuccess(notification.getSendOnSuccess())
        .withSendOnFailure(notification.getSendOnFailure())
        .withSlackConfiguration(toConfig(notification.getSlackConfiguration()));
  }

  private static io.airbyte.config.SlackNotificationConfiguration toConfig(final io.airbyte.api.model.SlackNotificationConfiguration notification) {
    return new io.airbyte.config.SlackNotificationConfiguration()
        .withWebhook(notification.getWebhook());
  }

  public static List<io.airbyte.api.model.NotificationLegacy> toApiList(final List<io.airbyte.config.NotificationLegacy> notifications) {
    return notifications.stream().map(NotificationConverter::toApi).collect(Collectors.toList());
  }

  public static io.airbyte.api.model.NotificationLegacy toApi(final io.airbyte.config.NotificationLegacy notification) {
    return new io.airbyte.api.model.NotificationLegacy()
        .notificationType(Enums.convertTo(notification.getNotificationType(), io.airbyte.api.model.NotificationType.class))
        .sendOnSuccess(notification.getSendOnSuccess())
        .sendOnFailure(notification.getSendOnFailure())
        .slackConfiguration(toApi(notification.getSlackConfiguration()));
  }

  private static io.airbyte.api.model.SlackNotificationConfiguration toApi(final io.airbyte.config.SlackNotificationConfiguration notification) {
    return new io.airbyte.api.model.SlackNotificationConfiguration()
        .webhook(notification.getWebhook());
  }

}
