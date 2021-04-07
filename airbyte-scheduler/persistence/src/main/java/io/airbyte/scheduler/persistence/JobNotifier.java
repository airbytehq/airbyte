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

package io.airbyte.scheduler.persistence;

import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.notification.NotificationClient;
import io.airbyte.notification.SlackNotificationClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobNotifier {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobNotifier.class);

  public static final String NOTIFICATION_TEST_MESSAGE = "Hello World! This is a test trying to send a message from Airbyte...";

  private final String connectionPageUrl;
  private final ConfigRepository configRepository;

  public JobNotifier(String webappUrl, ConfigRepository configRepository) {
    if (webappUrl.endsWith("/")) {
      this.connectionPageUrl = String.format("%ssource/connection/", webappUrl);
    } else {
      this.connectionPageUrl = String.format("%s/source/connection/", webappUrl);
    }
    this.configRepository = configRepository;
  }

  public boolean sendTestNotifications(final StandardWorkspace workspace) {
    boolean hasFailure = false;
    for (Notification notification : workspace.getNotifications()) {
      final NotificationClient notificationClient = getNotificationClient(notification);
      try {
        if (!notificationClient.notify(NOTIFICATION_TEST_MESSAGE)) {
          hasFailure = true;
        }
      } catch (InterruptedException | IOException e) {
        LOGGER.error("Failed to notify: {} due to {}", notification, e);
        hasFailure = true;
      }
    }
    return !hasFailure;
  }

  public void failJob(final String reason, final Job job) {
    final UUID connectionId = UUID.fromString(job.getScope());
    final UUID sourceDefinitionId = configRepository.getSourceDefinitionFromConnection(connectionId).getSourceDefinitionId();
    final UUID destinationDefinitionId = configRepository.getDestinationDefinitionFromConnection(connectionId).getDestinationDefinitionId();
    try {
      final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
      final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
      final Instant jobStartedDate = Instant.ofEpochSecond(job.getStartedAtInSecond().orElse(job.getCreatedAtInSecond()));
      final Instant jobUpdatedDate = Instant.ofEpochSecond(job.getUpdatedAtInSecond());
      final Duration duration = Duration.between(jobStartedDate, jobUpdatedDate);
      final String durationString = formatDurationPart(duration.toDaysPart(), "day")
          + formatDurationPart(duration.toHoursPart(), "hour")
          + formatDurationPart(duration.toMinutesPart(), "minute")
          + formatDurationPart(duration.toSecondsPart(), "second");
      final String sourceConnector = String.format("%s version %s", sourceDefinition.getName(), sourceDefinition.getDockerImageTag());
      final String destinationConnector = String.format("%s version %s", destinationDefinition.getName(), destinationDefinition.getDockerImageTag());
      final String jobDescription = String.format("sync started at %s, running for%s, as the %s.", jobStartedDate, durationString, reason);
      final String logUrl = connectionPageUrl + connectionId.toString();
      final StandardWorkspace workspace = configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true);
      for (Notification notification : workspace.getNotifications()) {
        final NotificationClient notificationClient = getNotificationClient(notification);
        try {
          if (!notificationClient.notifyJobFailure(sourceConnector, destinationConnector, jobDescription, logUrl)) {
            LOGGER.warn("Failed to successfully notify: {}", notification);
          }
        } catch (InterruptedException | IOException e) {
          LOGGER.error("Failed to notify: {} due to an exception", notification, e);
        }
      }
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      LOGGER.error("Unable to read configuration:", e);
    }
  }

  protected NotificationClient getNotificationClient(final Notification notification) {
    if (notification.getNotificationType() == NotificationType.SLACK) {
      return new SlackNotificationClient(notification.getSlackConfiguration());
    } else {
      throw new IllegalArgumentException("Unknown notification type:" + notification.getNotificationType());
    }
  }

  private static String formatDurationPart(long durationPart, String timeUnit) {
    if (durationPart == 1) {
      return String.format(" %s %s", durationPart, timeUnit);
    } else if (durationPart > 1) {
      // Use plural timeUnit
      return String.format(" %s %ss", durationPart, timeUnit);
    }
    return "";
  }

}
