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

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.notification.NotificationClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.FormatStyle;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobNotifierTest {

  private static final String WEBAPP_URL = "http://localhost:8000";
  private static final Instant NOW = Instant.now();
  private static final String TEST_DOCKER_REPO = "airbyte/test-image";
  private static final String TEST_DOCKER_TAG = "0.1.0";
  private static final UUID WORKSPACE_ID = UUID.randomUUID();

  private ConfigRepository configRepository;
  private WorkspaceHelper workspaceHelper;
  private JobNotifier jobNotifier;
  private NotificationClient notificationClient;
  private TrackingClient trackingClient;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    trackingClient = mock(TrackingClient.class);

    jobNotifier = spy(new JobNotifier(WEBAPP_URL, configRepository, workspaceHelper, trackingClient));
    notificationClient = mock(NotificationClient.class);
    when(jobNotifier.getNotificationClient(getSlackNotification())).thenReturn(notificationClient);
  }

  @Test
  void testFailJob() throws IOException, InterruptedException, JsonValidationException, ConfigNotFoundException {
    final Job job = createJob();
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withName("source-test")
        .withDockerRepository(TEST_DOCKER_REPO)
        .withDockerImageTag(TEST_DOCKER_TAG)
        .withSourceDefinitionId(UUID.randomUUID());
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withName("destination-test")
        .withDockerRepository(TEST_DOCKER_REPO)
        .withDockerImageTag(TEST_DOCKER_TAG)
        .withDestinationDefinitionId(UUID.randomUUID());
    when(configRepository.getSourceDefinitionFromConnection(any())).thenReturn(sourceDefinition);
    when(configRepository.getDestinationDefinitionFromConnection(any())).thenReturn(destinationDefinition);
    when(configRepository.getStandardSourceDefinition(any())).thenReturn(sourceDefinition);
    when(configRepository.getStandardDestinationDefinition(any())).thenReturn(destinationDefinition);
    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true)).thenReturn(getWorkspace());
    when(workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(job.getId())).thenReturn(WORKSPACE_ID);
    when(notificationClient.notifyJobFailure(anyString(), anyString(), anyString(), anyString())).thenReturn(true);

    jobNotifier.failJob("JobNotifierTest was running", job);
    final DateTimeFormatter formatter = DateTimeFormatter.ofLocalizedDateTime(FormatStyle.FULL).withZone(ZoneId.systemDefault());
    verify(notificationClient).notifyJobFailure(
        "source-test version 0.1.0",
        "destination-test version 0.1.0",
        String.format("sync started on %s, running for 1 day 10 hours 17 minutes 36 seconds, as the JobNotifierTest was running.",
            formatter.format(Instant.ofEpochSecond(job.getStartedAtInSecond().get()))),
        "http://localhost:8000/connections/" + job.getScope());

    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connection_id", UUID.fromString(job.getScope()));
    metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
    metadata.put("connector_source", "source-test");
    metadata.put("connector_source_version", TEST_DOCKER_TAG);
    metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());
    metadata.put("connector_destination", "destination-test");
    metadata.put("connector_destination_version", TEST_DOCKER_TAG);
    metadata.put("notification_type", NotificationType.SLACK);
    verify(trackingClient).track(WORKSPACE_ID, JobNotifier.FAILURE_NOTIFICATION, metadata.build());
  }

  private static StandardWorkspace getWorkspace() {
    return new StandardWorkspace()
        .withCustomerId(UUID.randomUUID())
        .withNotifications(List.of(getSlackNotification()));
  }

  private static Job createJob() {
    return new Job(
        10L,
        ConfigType.SYNC,
        UUID.randomUUID().toString(),
        new JobConfig(),
        Collections.emptyList(),
        JobStatus.FAILED,
        NOW.getEpochSecond(),
        NOW.getEpochSecond(),
        NOW.getEpochSecond() + 123456L);
  }

  private static Notification getSlackNotification() {
    return new Notification()
        .withNotificationType(NotificationType.SLACK)
        .withSlackConfiguration(new SlackNotificationConfiguration()
            .withWebhook("http://random.webhook.url/hooks.slack.com/"));
  }

}
