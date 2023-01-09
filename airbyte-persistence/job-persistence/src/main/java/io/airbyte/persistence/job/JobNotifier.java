/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job;

import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.notification.NotificationClient;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.tracker.TrackingMetadata;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.FormatStyle;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.lang3.time.DurationFormatUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobNotifier {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobNotifier.class);

  public static final String FAILURE_NOTIFICATION = "Failure Notification";
  public static final String SUCCESS_NOTIFICATION = "Success Notification";
  public static final String CONNECTION_DISABLED_WARNING_NOTIFICATION = "Connection Disabled Warning Notification";
  public static final String CONNECTION_DISABLED_NOTIFICATION = "Connection Disabled Notification";

  private final ConfigRepository configRepository;
  private final TrackingClient trackingClient;
  private final WebUrlHelper webUrlHelper;
  private final WorkspaceHelper workspaceHelper;

  public JobNotifier(final WebUrlHelper webUrlHelper,
                     final ConfigRepository configRepository,
                     final WorkspaceHelper workspaceHelper,
                     final TrackingClient trackingClient) {
    this.webUrlHelper = webUrlHelper;
    this.workspaceHelper = workspaceHelper;
    this.configRepository = configRepository;
    this.trackingClient = trackingClient;
  }

  private void notifyJob(final String reason, final String action, final Job job) {
    try {
      final UUID workspaceId = workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(job.getId());
      final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, true);
      notifyJob(reason, action, job, workspaceId, workspace, workspace.getNotifications());
    } catch (final Exception e) {
      LOGGER.error("Unable to read configuration:", e);
    }
  }

  private void notifyJob(final String reason,
                         final String action,
                         final Job job,
                         final UUID workspaceId,
                         final StandardWorkspace workspace,
                         final List<Notification> notifications) {
    final UUID connectionId = UUID.fromString(job.getScope());
    try {
      final StandardSourceDefinition sourceDefinition = configRepository.getSourceDefinitionFromConnection(connectionId);
      final StandardDestinationDefinition destinationDefinition = configRepository.getDestinationDefinitionFromConnection(connectionId);
      final String sourceConnector = sourceDefinition.getName();
      final String destinationConnector = destinationDefinition.getName();
      final String failReason = Strings.isNullOrEmpty(reason) ? "" : String.format(", as the %s", reason);
      final String jobDescription = getJobDescription(job, failReason);
      final String logUrl = webUrlHelper.getConnectionUrl(workspaceId, connectionId);
      final Map<String, Object> jobMetadata = TrackingMetadata.generateJobAttemptMetadata(job);
      final Map<String, Object> sourceMetadata = TrackingMetadata.generateSourceDefinitionMetadata(sourceDefinition);
      final Map<String, Object> destinationMetadata = TrackingMetadata.generateDestinationDefinitionMetadata(destinationDefinition);
      for (final Notification notification : notifications) {
        final NotificationClient notificationClient = getNotificationClient(notification);
        try {
          final Builder<String, Object> notificationMetadata = ImmutableMap.builder();
          notificationMetadata.put("connection_id", connectionId);
          if (NotificationType.SLACK.equals(notification.getNotificationType()) &&
              notification.getSlackConfiguration().getWebhook().contains("hooks.slack.com")) {
            // flag as slack if the webhook URL is also pointing to slack
            notificationMetadata.put("notification_type", NotificationType.SLACK);
          } else if (NotificationType.CUSTOMERIO.equals(notification.getNotificationType())) {
            notificationMetadata.put("notification_type", NotificationType.CUSTOMERIO);
          } else {
            // Slack Notification type could be "hacked" and re-used for custom webhooks
            notificationMetadata.put("notification_type", "N/A");
          }
          trackingClient.track(
              workspaceId,
              action,
              MoreMaps.merge(jobMetadata, sourceMetadata, destinationMetadata, notificationMetadata.build()));

          if (FAILURE_NOTIFICATION.equalsIgnoreCase(action)) {
            if (!notificationClient.notifyJobFailure(sourceConnector, destinationConnector, jobDescription, logUrl, job.getId())) {
              LOGGER.warn("Failed to successfully notify failure: {}", notification);
            }
            break;
          } else if (SUCCESS_NOTIFICATION.equalsIgnoreCase(action)) {
            if (!notificationClient.notifyJobSuccess(sourceConnector, destinationConnector, jobDescription, logUrl, job.getId())) {
              LOGGER.warn("Failed to successfully notify success: {}", notification);
            }
            break;
          } else if (CONNECTION_DISABLED_NOTIFICATION.equalsIgnoreCase(action)) {
            if (!notificationClient.notifyConnectionDisabled(workspace.getEmail(), sourceConnector, destinationConnector, jobDescription,
                workspaceId, connectionId)) {
              LOGGER.warn("Failed to successfully notify auto-disable connection: {}", notification);
            }
            break;
          } else if (CONNECTION_DISABLED_WARNING_NOTIFICATION.equalsIgnoreCase(action)) {
            if (!notificationClient.notifyConnectionDisableWarning(workspace.getEmail(), sourceConnector, destinationConnector, jobDescription,
                workspaceId, connectionId)) {
              LOGGER.warn("Failed to successfully notify auto-disable connection warning: {}", notification);
            }

          }
        } catch (final Exception e) {
          LOGGER.error("Failed to notify: {} due to an exception", notification, e);
        }
      }
    } catch (final Exception e) {
      LOGGER.error("Unable to read configuration:", e);
    }
  }

  // This method allows for the alert to be sent without the customerio configuration set in the
  // database
  // This is only needed because there is no UI element to allow for users to create that
  // configuration.
  // Once that exists, this can be removed and we should be using `notifyJobByEmail`.
  // The alert is sent to the email associated with the workspace.
  public void notifyJobByEmail(final String reason, final String action, final Job job) {
    final Notification emailNotification = new Notification();
    emailNotification.setNotificationType(NotificationType.CUSTOMERIO);
    try {
      final UUID workspaceId = workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(job.getId());
      final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, true);
      notifyJob(reason, action, job, workspaceId, workspace, Collections.singletonList(emailNotification));
    } catch (final Exception e) {
      LOGGER.error("Unable to read configuration:", e);
    }
  }

  private String getJobDescription(final Job job, final String reason) {
    final Instant jobStartedDate = Instant.ofEpochSecond(job.getStartedAtInSecond().orElse(job.getCreatedAtInSecond()));
    final DateTimeFormatter formatter = DateTimeFormatter.ofLocalizedDateTime(FormatStyle.FULL).withZone(ZoneId.systemDefault());
    final Instant jobUpdatedDate = Instant.ofEpochSecond(job.getUpdatedAtInSecond());
    final Instant adjustedJobUpdatedDate = jobUpdatedDate.equals(jobStartedDate) ? Instant.now() : jobUpdatedDate;
    final Duration duration = Duration.between(jobStartedDate, adjustedJobUpdatedDate);
    final String durationString = DurationFormatUtils.formatDurationWords(duration.toMillis(), true, true);

    return String.format("sync started on %s, running for %s%s.", formatter.format(jobStartedDate), durationString, reason);
  }

  public void failJob(final String reason, final Job job) {
    notifyJob(reason, FAILURE_NOTIFICATION, job);
  }

  public void successJob(final Job job) {
    notifyJob(null, SUCCESS_NOTIFICATION, job);
  }

  public void autoDisableConnection(final Job job) {
    notifyJob(null, CONNECTION_DISABLED_NOTIFICATION, job);
  }

  public void autoDisableConnectionWarning(final Job job) {
    notifyJob(null, CONNECTION_DISABLED_WARNING_NOTIFICATION, job);
  }

  protected NotificationClient getNotificationClient(final Notification notification) {
    return NotificationClient.createNotificationClient(notification);
  }

}
