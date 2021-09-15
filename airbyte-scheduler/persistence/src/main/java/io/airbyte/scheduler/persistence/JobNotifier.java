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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.notification.NotificationClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.job_tracker.TrackingMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.FormatStyle;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobNotifier {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobNotifier.class);

  public static final String FAILURE_NOTIFICATION = "Failure Notification";
  public static final String SUCCESS_NOTIFICATION = "Success Notification";

  private final String connectionPageUrl;
  private final ConfigRepository configRepository;
  private final TrackingClient trackingClient;
  private final WorkspaceHelper workspaceHelper;

  public JobNotifier(String webappUrl, ConfigRepository configRepository, WorkspaceHelper workspaceHelper) {
    this(webappUrl, configRepository, workspaceHelper, TrackingClientSingleton.get());
  }

  @VisibleForTesting
  JobNotifier(String webappUrl, ConfigRepository configRepository, WorkspaceHelper workspaceHelper, TrackingClient trackingClient) {
    this.workspaceHelper = workspaceHelper;
    if (webappUrl.endsWith("/")) {
      this.connectionPageUrl = String.format("%sconnections/", webappUrl);
    } else {
      this.connectionPageUrl = String.format("%s/connections/", webappUrl);
    }
    this.configRepository = configRepository;
    this.trackingClient = trackingClient;
  }

  private void notifyJob(final String reason, final String action, final Job job) {
    final UUID connectionId = UUID.fromString(job.getScope());
    final UUID sourceDefinitionId = configRepository.getSourceDefinitionFromConnection(connectionId).getSourceDefinitionId();
    final UUID destinationDefinitionId = configRepository.getDestinationDefinitionFromConnection(connectionId).getDestinationDefinitionId();
    try {
      final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
      final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
      final Instant jobStartedDate = Instant.ofEpochSecond(job.getStartedAtInSecond().orElse(job.getCreatedAtInSecond()));
      final DateTimeFormatter formatter = DateTimeFormatter.ofLocalizedDateTime(FormatStyle.FULL).withZone(ZoneId.systemDefault());
      final Instant jobUpdatedDate = Instant.ofEpochSecond(job.getUpdatedAtInSecond());
      final Instant adjustedJobUpdatedDate = jobUpdatedDate.equals(jobStartedDate) ? Instant.now() : jobUpdatedDate;
      final Duration duration = Duration.between(jobStartedDate, adjustedJobUpdatedDate);
      final String durationString = formatDurationPart(duration.toDaysPart(), "day")
          + formatDurationPart(duration.toHoursPart(), "hour")
          + formatDurationPart(duration.toMinutesPart(), "minute")
          + formatDurationPart(duration.toSecondsPart(), "second");
      final String sourceConnector = String.format("%s version %s", sourceDefinition.getName(), sourceDefinition.getDockerImageTag());
      final String destinationConnector = String.format("%s version %s", destinationDefinition.getName(), destinationDefinition.getDockerImageTag());
      final String failReason = Strings.isNullOrEmpty(reason) ? "" : String.format(", as the %s", reason);
      final String jobDescription =
          String.format("sync started on %s, running for%s%s.", formatter.format(jobStartedDate), durationString, failReason);
      final String logUrl = connectionPageUrl + connectionId;
      final UUID workspaceId = workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(job.getId());
      final StandardWorkspace workspace = configRepository.getStandardWorkspace(workspaceId, true);
      final ImmutableMap<String, Object> jobMetadata = TrackingMetadata.generateJobAttemptMetadata(job);
      final ImmutableMap<String, Object> sourceMetadata = TrackingMetadata.generateSourceDefinitionMetadata(sourceDefinition);
      final ImmutableMap<String, Object> destinationMetadata = TrackingMetadata.generateDestinationDefinitionMetadata(destinationDefinition);
      for (Notification notification : workspace.getNotifications()) {
        final NotificationClient notificationClient = getNotificationClient(notification);
        try {
          final Builder<String, Object> notificationMetadata = ImmutableMap.builder();
          notificationMetadata.put("connection_id", connectionId);
          if (notification.getNotificationType().equals(NotificationType.SLACK) &&
              notification.getSlackConfiguration().getWebhook().contains("hooks.slack.com")) {
            // flag as slack if the webhook URL is also pointing to slack
            notificationMetadata.put("notification_type", NotificationType.SLACK);
          } else {
            // Slack Notification type could be "hacked" and re-used for custom webhooks
            notificationMetadata.put("notification_type", "N/A");
          }
          trackingClient.track(
              workspaceId,
              action,
              MoreMaps.merge(jobMetadata, sourceMetadata, destinationMetadata, notificationMetadata.build()));
          if (FAILURE_NOTIFICATION.equals(action)) {
            if (!notificationClient.notifyJobFailure(sourceConnector, destinationConnector, jobDescription, logUrl)) {
              LOGGER.warn("Failed to successfully notify failure: {}", notification);
            }
          } else if (SUCCESS_NOTIFICATION.equals(action)) {
            if (!notificationClient.notifyJobSuccess(sourceConnector, destinationConnector, jobDescription, logUrl)) {
              LOGGER.warn("Failed to successfully notify success: {}", notification);
            }
          }
        } catch (InterruptedException | IOException e) {
          LOGGER.error("Failed to notify: {} due to an exception", notification, e);
        }
      }
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      LOGGER.error("Unable to read configuration:", e);
    }
  }

  public void failJob(final String reason, final Job job) {
    notifyJob(reason, FAILURE_NOTIFICATION, job);
  }

  public void successJob(final Job job) {
    notifyJob(null, SUCCESS_NOTIFICATION, job);
  }

  protected NotificationClient getNotificationClient(final Notification notification) {
    return NotificationClient.createNotificationClient(notification);
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
