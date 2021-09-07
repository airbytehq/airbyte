/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.converters;

import io.airbyte.commons.enums.Enums;
import java.util.List;
import java.util.stream.Collectors;

public class NotificationConverter {

  public static List<io.airbyte.config.Notification> toConfigList(final List<io.airbyte.api.model.Notification> notifications) {
    return notifications.stream().map(NotificationConverter::toConfig).collect(Collectors.toList());
  }

  public static io.airbyte.config.Notification toConfig(final io.airbyte.api.model.Notification notification) {
    return new io.airbyte.config.Notification()
        .withNotificationType(Enums.convertTo(notification.getNotificationType(), io.airbyte.config.Notification.NotificationType.class))
        .withSendOnSuccess(notification.getSendOnSuccess())
        .withSendOnFailure(notification.getSendOnFailure())
        .withSlackConfiguration(toConfig(notification.getSlackConfiguration()));
  }

  private static io.airbyte.config.SlackNotificationConfiguration toConfig(final io.airbyte.api.model.SlackNotificationConfiguration notification) {
    return new io.airbyte.config.SlackNotificationConfiguration()
        .withWebhook(notification.getWebhook());
  }

  public static List<io.airbyte.api.model.Notification> toApiList(final List<io.airbyte.config.Notification> notifications) {
    return notifications.stream().map(NotificationConverter::toApi).collect(Collectors.toList());
  }

  public static io.airbyte.api.model.Notification toApi(final io.airbyte.config.Notification notification) {
    return new io.airbyte.api.model.Notification()
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
