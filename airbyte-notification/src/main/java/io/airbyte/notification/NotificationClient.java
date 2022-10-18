/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.notification;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Notification;
import java.io.IOException;
import java.util.UUID;

public abstract class NotificationClient {

  protected boolean sendOnSuccess;
  protected boolean sendOnFailure;

  public NotificationClient(final Notification notification) {
    this.sendOnSuccess = notification.getSendOnSuccess();
    this.sendOnFailure = notification.getSendOnFailure();
  }

  public abstract boolean notifyJobFailure(
                                           String sourceConnector,
                                           String destinationConnector,
                                           String jobDescription,
                                           String logUrl,
                                           Long jobId)
      throws IOException, InterruptedException;

  public abstract boolean notifyJobSuccess(
                                           String sourceConnector,
                                           String destinationConnector,
                                           String jobDescription,
                                           String logUrl,
                                           Long jobId)
      throws IOException, InterruptedException;

  public abstract boolean notifyConnectionDisabled(String receiverEmail,
                                                   String sourceConnector,
                                                   String destinationConnector,
                                                   String jobDescription,
                                                   UUID workspaceId,
                                                   UUID connectionId)
      throws IOException, InterruptedException;

  public abstract boolean notifyConnectionDisableWarning(String receiverEmail,
                                                         String sourceConnector,
                                                         String destinationConnector,
                                                         String jobDescription,
                                                         UUID workspaceId,
                                                         UUID connectionId)
      throws IOException, InterruptedException;

  public abstract boolean notifySuccess(String message) throws IOException, InterruptedException;

  public abstract boolean notifyFailure(String message) throws IOException, InterruptedException;

  public static NotificationClient createNotificationClient(final Notification notification) {
    return switch (notification.getNotificationType()) {
      case SLACK -> new SlackNotificationClient(notification);
      case CUSTOMERIO -> new CustomerioNotificationClient(notification);
      default -> throw new IllegalArgumentException("Unknown notification type:" + notification.getNotificationType());
    };
  }

  String renderTemplate(final String templateFile, final String... data) throws IOException {
    final String template = MoreResources.readResource(templateFile);
    return String.format(template, data);
  }

}
