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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.util.Strings;

public class JobTracker {

  public enum JobState {
    STARTED,
    SUCCEEDED,
    FAILED
  }

  public static final String MESSAGE_NAME = "Connector Jobs";

  private final ConfigRepository configRepository;
  private final JobPersistence jobPersistence;
  private final TrackingClient trackingClient;

  public JobTracker(ConfigRepository configRepository, JobPersistence jobPersistence) {
    this(configRepository, jobPersistence, TrackingClientSingleton.get());
  }

  @VisibleForTesting
  JobTracker(ConfigRepository configRepository, JobPersistence jobPersistence, TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.jobPersistence = jobPersistence;
    this.trackingClient = trackingClient;
  }

  public void trackCheckConnectionSource(UUID jobId, UUID sourceDefinitionId, JobState jobState, StandardCheckConnectionOutput output) {
    Exceptions.swallow(() -> {
      final ImmutableMap<String, Object> checkConnMetadata = generateCheckConnectionMetadata(output);
      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(jobId.toString(), ConfigType.CHECK_CONNECTION_SOURCE);
      final ImmutableMap<String, Object> sourceDefMetadata = generateSourceDefinitionMetadata(sourceDefinitionId);
      final ImmutableMap<String, Object> stateMetadata = generateStateMetadata(jobState);

      track(MoreMaps.merge(checkConnMetadata, jobMetadata, sourceDefMetadata, stateMetadata));
    });
  }

  public void trackCheckConnectionDestination(UUID jobId, UUID destinationDefinitionId, JobState jobState, StandardCheckConnectionOutput output) {
    Exceptions.swallow(() -> {
      final ImmutableMap<String, Object> checkConnMetadata = generateCheckConnectionMetadata(output);
      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(jobId.toString(), ConfigType.CHECK_CONNECTION_DESTINATION);
      final ImmutableMap<String, Object> destinationDefinitionMetadata = generateDestinationDefinitionMetadata(destinationDefinitionId);
      final ImmutableMap<String, Object> stateMetadata = generateStateMetadata(jobState);

      track(MoreMaps.merge(checkConnMetadata, jobMetadata, destinationDefinitionMetadata, stateMetadata));
    });
  }

  public void trackDiscover(UUID jobId, UUID sourceDefinitionId, JobState jobState) {
    Exceptions.swallow(() -> {
      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(jobId.toString(), ConfigType.DISCOVER_SCHEMA);
      final ImmutableMap<String, Object> sourceDefMetadata = generateSourceDefinitionMetadata(sourceDefinitionId);
      final ImmutableMap<String, Object> stateMetadata = generateStateMetadata(jobState);

      track(MoreMaps.merge(jobMetadata, sourceDefMetadata, stateMetadata));
    });
  }

  // used for tracking all asynchronous jobs (sync and reset).
  public void trackSync(Job job, JobState jobState) {
    Exceptions.swallow(() -> {
      final ConfigType configType = job.getConfigType();
      Preconditions.checkArgument(configType == ConfigType.SYNC || configType == ConfigType.RESET_CONNECTION);
      final long jobId = job.getId();
      final UUID connectionId = UUID.fromString(job.getScope());
      final UUID sourceDefinitionId = configRepository.getSourceDefinitionFromConnection(connectionId).getSourceDefinitionId();
      final UUID destinationDefinitionId = configRepository.getDestinationDefinitionFromConnection(connectionId).getDestinationDefinitionId();

      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(String.valueOf(jobId), configType, job.getAttemptsCount());
      final ImmutableMap<String, Object> jobAttemptMetadata = generateJobAttemptMetadata(job.getId(), jobState);
      final ImmutableMap<String, Object> sourceDefMetadata = generateSourceDefinitionMetadata(sourceDefinitionId);
      final ImmutableMap<String, Object> destinationDefMetadata = generateDestinationDefinitionMetadata(destinationDefinitionId);
      final ImmutableMap<String, Object> syncMetadata = generateSyncMetadata(connectionId);
      final ImmutableMap<String, Object> stateMetadata = generateStateMetadata(jobState);

      track(MoreMaps.merge(jobMetadata, jobAttemptMetadata, sourceDefMetadata, destinationDefMetadata, syncMetadata, stateMetadata));
    });
  }

  private ImmutableMap<String, Object> generateSyncMetadata(UUID connectionId) throws ConfigNotFoundException, IOException, JsonValidationException {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connection_id", connectionId);

    final StandardSyncSchedule schedule = configRepository.getStandardSyncSchedule(connectionId);
    String frequencyString;
    if (schedule.getManual()) {
      frequencyString = "manual";
    } else {
      final long intervalInMinutes = TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(schedule.getSchedule()));
      frequencyString = intervalInMinutes + " min";
    }
    metadata.put("frequency", frequencyString);

    return metadata.build();
  }

  private static ImmutableMap<String, Object> generateStateMetadata(JobState jobState) {
    final Builder<String, Object> metadata = ImmutableMap.builder();

    switch (jobState) {
      case STARTED -> {
        metadata.put("attempt_stage", "STARTED");
      }
      case SUCCEEDED, FAILED -> {
        metadata.put("attempt_stage", "ENDED");
        metadata.put("attempt_completion_status", jobState);
      }
    }

    return metadata.build();
  }

  /**
   * The CheckConnection jobs (both source and destination) of the
   * {@link io.airbyte.scheduler.client.SynchronousSchedulerClient} interface can have a successful
   * job with a failed check. Because of this, tracking just the job attempt status does not capture
   * the whole picture. The `check_connection_outcome` field tracks this.
   */
  private ImmutableMap<String, Object> generateCheckConnectionMetadata(StandardCheckConnectionOutput output) {
    if (output == null) {
      return ImmutableMap.of();
    }
    Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("check_connection_outcome", output.getStatus().toString());
    return metadata.build();
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

  private ImmutableMap<String, Object> generateJobMetadata(String jobId, ConfigType configType) {
    return generateJobMetadata(jobId, configType, 0);
  }

  private ImmutableMap<String, Object> generateJobMetadata(String jobId, ConfigType configType, int attempt) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("job_type", configType);
    metadata.put("job_id", jobId);
    metadata.put("attempt_id", attempt);

    return metadata.build();
  }

  private ImmutableMap<String, Object> generateJobAttemptMetadata(long jobId, JobState jobState) throws IOException {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    final Job job = jobPersistence.getJob(jobId);
    if (jobState != JobState.STARTED && job != null) {
      final List<Attempt> attempts = job.getAttempts();
      if (attempts != null && !attempts.isEmpty()) {
        final Attempt lastAttempt = attempts.get(attempts.size() - 1);
        if (lastAttempt.getOutput() != null && lastAttempt.getOutput().isPresent()) {
          final JobOutput jobOutput = lastAttempt.getOutput().get();
          final StandardSyncSummary syncSummary = jobOutput.getSync().getStandardSyncSummary();
          metadata.put("duration", Math.round((syncSummary.getEndTime() - syncSummary.getStartTime()) / 1000.0));
          metadata.put("volume_mb", syncSummary.getBytesSynced());
          metadata.put("volume_rows", syncSummary.getRecordsSynced());
        }
      }
    }
    return metadata.build();
  }

  private void track(Map<String, Object> metadata) {
    trackingClient.track(MESSAGE_NAME, metadata);
  }

}
