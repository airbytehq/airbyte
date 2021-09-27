/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.notification;

import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import java.io.IOException;

public abstract class NotificationClient {

  protected boolean sendOnSuccess;
  protected boolean sendOnFailure;

  public NotificationClient(Notification notification) {
    this.sendOnSuccess = notification.getSendOnSuccess();
    this.sendOnFailure = notification.getSendOnFailure();
  }

  public abstract boolean notifyJobFailure(
                                           String sourceConnector,
                                           String destinationConnector,
                                           String jobDescription,
                                           String logUrl)
      throws IOException, InterruptedException;

  public abstract boolean notifyJobSuccess(
                                           String sourceConnector,
                                           String destinationConnector,
                                           String jobDescription,
                                           String logUrl)
      throws IOException, InterruptedException;

  public abstract boolean notifySuccess(String message) throws IOException, InterruptedException;

  public abstract boolean notifyFailure(String message) throws IOException, InterruptedException;

  public static NotificationClient createNotificationClient(final Notification notification) {
    if (notification.getNotificationType() == NotificationType.SLACK) {
      return new SlackNotificationClient(notification);
    } else {
      throw new IllegalArgumentException("Unknown notification type:" + notification.getNotificationType());
    }
  }

}
