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

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.map.MoreMaps;
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
import java.util.Map;
import java.util.UUID;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobNotifier {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobNotifier.class);

  private final String connectionPageUrl;
  private final ConfigRepository configRepository;

  public JobNotifier(String webappUrl, ConfigRepository configRepository) {
    this.connectionPageUrl = String.format("%s/source/connection/", webappUrl);
    this.configRepository = configRepository;
  }

  public void failJob(final String reason, final Job job) {
    final UUID connectionId = UUID.fromString(job.getScope());
    final UUID sourceDefinitionId = configRepository.getSourceDefinitionFromConnection(connectionId).getSourceDefinitionId();
    final UUID destinationDefinitionId = configRepository.getDestinationDefinitionFromConnection(connectionId).getDestinationDefinitionId();
    try {
      final ImmutableMap<String, Object> sourceDefMetadata = generateSourceDefinitionMetadata(sourceDefinitionId);
      final ImmutableMap<String, Object> destinationDefMetadata = generateDestinationDefinitionMetadata(destinationDefinitionId);
      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(reason, job);
      final Map<String, Object> metadata = MoreMaps.merge(sourceDefMetadata, destinationDefMetadata, jobMetadata);
      final StandardWorkspace workspace = configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true);

      for (Notification notification : workspace.getNotifications()) {
        final NotificationClient notificationClient = getNotificationClient(notification);
        try {
          notificationClient.notifyJobFailure(metadata);
        } catch (InterruptedException | IOException e) {
          LOGGER.error("Failed to notify: {} due to {}", notification, e);
        }
      }
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      LOGGER.error("Unable to read Workspace configuration");
    }
  }

  private NotificationClient getNotificationClient(final Notification notification) {
    if (notification.getNotificationType() == NotificationType.SLACK) {
      return new SlackNotificationClient(connectionPageUrl, notification.getSlackConfiguration());
    } else {
      throw new IllegalArgumentException("Unknown notification type:" + notification.getNotificationType());
    }
  }

  private ImmutableMap<String, Object> generateDestinationDefinitionMetadata(UUID destinationDefinitionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final Builder<String, Object> metadata = ImmutableMap.builder();

    final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    metadata.put("connector_destination", destinationDefinition.getName());
    metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());
    final String imageTag = destinationDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_destination_version", imageTag);
    }
    return metadata.build();
  }

  private ImmutableMap<String, Object> generateSourceDefinitionMetadata(UUID sourceDefinitionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final Builder<String, Object> metadata = ImmutableMap.builder();

    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    metadata.put("connector_source", sourceDefinition.getName());
    metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
    final String imageTag = sourceDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_source_version", imageTag);
    }
    return metadata.build();
  }

  private static ImmutableMap<String, Object> generateJobMetadata(final String reason, final Job job)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = UUID.fromString(job.getScope());
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connection_id", connectionId);
    metadata.put("failure_reason", reason);
    final Instant jobStartedDate = Instant.ofEpochSecond(job.getStartedAtInSecond().orElse(job.getCreatedAtInSecond()));
    metadata.put("started_at", jobStartedDate);
    final Instant jobUpdatedDate = Instant.ofEpochSecond(job.getUpdatedAtInSecond());
    final Duration duration = Duration.between(jobStartedDate, jobUpdatedDate);
    final String durationString = formatDurationPart(duration.toDaysPart(), "day")
        + formatDurationPart(duration.toHoursPart(), "hour")
        + formatDurationPart(duration.toMinutesPart(), "minute")
        + formatDurationPart(duration.toSecondsPart(), "second");
    metadata.put("duration", durationString);
    return metadata.build();
  }

  private static String formatDurationPart(long durationPart, String timeUnit) {
    if (durationPart == 1) {
      return String.format("%s %s", durationPart, timeUnit);
    } else if (durationPart > 1) {
      return String.format("%s %ss", durationPart, timeUnit);
    }
    return "";
  }

}
