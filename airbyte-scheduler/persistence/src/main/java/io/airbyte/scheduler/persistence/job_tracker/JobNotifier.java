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

package io.airbyte.scheduler.persistence.job_tracker;

import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.notification.NotificationClient;
import io.airbyte.notification.SlackNotificationClient;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobNotifier {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobNotifier.class);

  private final ConfigRepository configRepository;

  public JobNotifier(ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public void notifyJobCompletion(JobState jobState, Map<String, Object> metadata) {
    try {
      final StandardWorkspace workspace = configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true);
      for (Notification notification : workspace.getNotifications()) {
        final NotificationClient notificationClient = getNotificationClient(notification);
        try {
          if (jobState.equals(JobState.SUCCEEDED)) {
            notificationClient.notifyJobSuccess(metadata);
          } else if (jobState.equals(JobState.FAILED)) {
            notificationClient.notifyJobFailure(metadata);
          }
        } catch (InterruptedException | IOException e) {
          LOGGER.error("Failed to notify: {} due to {}", notification, e);
        }
      }
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      LOGGER.error("Unable to read Workspace configuration");
    }
  }

  private static NotificationClient getNotificationClient(final Notification notification) {
    if (notification.getNotificationType() == NotificationType.SLACK) {
      return new SlackNotificationClient(notification);
    } else {
      throw new IllegalArgumentException("Unknown notification type:" + notification.getNotificationType());
    }
  }

}
