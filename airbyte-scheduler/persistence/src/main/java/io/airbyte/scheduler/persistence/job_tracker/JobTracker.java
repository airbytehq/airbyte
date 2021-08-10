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

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

public class JobTracker {

  public enum JobState {
    STARTED,
    SUCCEEDED,
    FAILED
  }

  public static final String MESSAGE_NAME = "Connector Jobs";
  public static final String CONFIG = "config";
  public static final String CATALOG = "catalog";
  public static final String OPERATION = "operation.";
  public static final String SET = "set";

  private final ConfigRepository configRepository;
  private final JobPersistence jobPersistence;
  private final WorkspaceHelper workspaceHelper;
  private final TrackingClient trackingClient;

  public JobTracker(ConfigRepository configRepository, JobPersistence jobPersistence) {
    this(configRepository, jobPersistence, new WorkspaceHelper(configRepository, jobPersistence), TrackingClientSingleton.get());
  }

  @VisibleForTesting
  JobTracker(ConfigRepository configRepository, JobPersistence jobPersistence, WorkspaceHelper workspaceHelper, TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.jobPersistence = jobPersistence;
    this.workspaceHelper = workspaceHelper;
    this.trackingClient = trackingClient;
  }

  public void trackCheckConnectionSource(UUID jobId,
                                         UUID sourceDefinitionId,
                                         UUID workspaceId,
                                         JobState jobState,
                                         StandardCheckConnectionOutput output) {
    Exceptions.swallow(() -> {
      final ImmutableMap<String, Object> checkConnMetadata = generateCheckConnectionMetadata(output);
      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(jobId.toString(), ConfigType.CHECK_CONNECTION_SOURCE);
      final ImmutableMap<String, Object> sourceDefMetadata = generateSourceDefinitionMetadata(sourceDefinitionId);
      final ImmutableMap<String, Object> stateMetadata = generateStateMetadata(jobState);

      track(workspaceId, MoreMaps.merge(checkConnMetadata, jobMetadata, sourceDefMetadata, stateMetadata));
    });
  }

  public void trackCheckConnectionDestination(UUID jobId,
                                              UUID destinationDefinitionId,
                                              UUID workspaceId,
                                              JobState jobState,
                                              StandardCheckConnectionOutput output) {
    Exceptions.swallow(() -> {
      final ImmutableMap<String, Object> checkConnMetadata = generateCheckConnectionMetadata(output);
      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(jobId.toString(), ConfigType.CHECK_CONNECTION_DESTINATION);
      final ImmutableMap<String, Object> destinationDefinitionMetadata = generateDestinationDefinitionMetadata(destinationDefinitionId);
      final ImmutableMap<String, Object> stateMetadata = generateStateMetadata(jobState);

      track(workspaceId, MoreMaps.merge(checkConnMetadata, jobMetadata, destinationDefinitionMetadata, stateMetadata));
    });
  }

  public void trackDiscover(UUID jobId, UUID sourceDefinitionId, UUID workspaceId, JobState jobState) {
    Exceptions.swallow(() -> {
      final ImmutableMap<String, Object> jobMetadata = generateJobMetadata(jobId.toString(), ConfigType.DISCOVER_SCHEMA);
      final ImmutableMap<String, Object> sourceDefMetadata = generateSourceDefinitionMetadata(sourceDefinitionId);
      final ImmutableMap<String, Object> stateMetadata = generateStateMetadata(jobState);

      track(workspaceId, MoreMaps.merge(jobMetadata, sourceDefMetadata, stateMetadata));
    });
  }

  // used for tracking all asynchronous jobs (sync and reset).
  public void trackSync(Job job, JobState jobState) {
    Exceptions.swallow(() -> {
      final ConfigType configType = job.getConfigType();
      final boolean allowedJob = configType == ConfigType.SYNC || configType == ConfigType.RESET_CONNECTION;
      Preconditions.checkArgument(allowedJob, "Job type " + configType + " is not allowed!");
      final long jobId = job.getId();
      final UUID connectionId = UUID.fromString(job.getScope());
      final UUID sourceDefinitionId = configRepository.getSourceDefinitionFromConnection(connectionId).getSourceDefinitionId();
      final UUID destinationDefinitionId = configRepository.getDestinationDefinitionFromConnection(connectionId).getDestinationDefinitionId();

      final Map<String, Object> jobMetadata = generateJobMetadata(String.valueOf(jobId), configType, job.getAttemptsCount());
      final Map<String, Object> jobAttemptMetadata = generateJobAttemptMetadata(job.getId(), jobState);
      final Map<String, Object> sourceDefMetadata = generateSourceDefinitionMetadata(sourceDefinitionId);
      final Map<String, Object> destinationDefMetadata = generateDestinationDefinitionMetadata(destinationDefinitionId);
      final Map<String, Object> syncMetadata = generateSyncMetadata(connectionId);
      final Map<String, Object> stateMetadata = generateStateMetadata(jobState);
      final Map<String, Object> syncConfigMetadata = generateSyncConfigMetadata(job.getConfig());

      final UUID workspaceId = workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(jobId);
      track(workspaceId,
          MoreMaps.merge(
              jobMetadata,
              jobAttemptMetadata,
              sourceDefMetadata,
              destinationDefMetadata,
              syncMetadata,
              stateMetadata,
              syncConfigMetadata));
    });
  }

  private Map<String, Object> generateSyncConfigMetadata(JobConfig config) {
    if (config.getConfigType() == ConfigType.SYNC) {
      JsonNode sourceConfiguration = config.getSync().getSourceConfiguration();
      JsonNode destinationConfiguration = config.getSync().getDestinationConfiguration();

      Map<String, Object> sourceMetadata = configToMetadata(CONFIG + ".source", sourceConfiguration);
      Map<String, Object> destinationMetadata = configToMetadata(CONFIG + ".destination", destinationConfiguration);
      Map<String, Object> catalogMetadata = getCatalogMetadata(config.getSync().getConfiguredAirbyteCatalog());

      return MoreMaps.merge(sourceMetadata, destinationMetadata, catalogMetadata);
    } else {
      return Collections.emptyMap();
    }
  }

  private Map<String, Object> getCatalogMetadata(ConfiguredAirbyteCatalog catalog) {
    final Map<String, Object> output = new HashMap<>();

    for (ConfiguredAirbyteStream stream : catalog.getStreams()) {
      output.put(CATALOG + ".sync_mode." + stream.getSyncMode().name().toLowerCase(), SET);
      output.put(CATALOG + ".destination_sync_mode." + stream.getDestinationSyncMode().name().toLowerCase(), SET);
    }

    return output;
  }

  protected static Map<String, Object> configToMetadata(String jsonPath, JsonNode config) {
    final Map<String, Object> output = new HashMap<>();

    if (config.isObject()) {
      final ObjectNode node = (ObjectNode) config;
      for (Iterator<Map.Entry<String, JsonNode>> it = node.fields(); it.hasNext();) {
        var entry = it.next();
        var field = entry.getKey();
        var fieldJsonPath = jsonPath + "." + field;
        var child = entry.getValue();

        if (child.isBoolean()) {
          output.put(fieldJsonPath, child.asBoolean());
        } else if (!child.isNull()) {
          if (child.isObject()) {
            output.putAll(configToMetadata(fieldJsonPath, child));
          } else if (!child.isTextual() || (child.isTextual() && !child.asText().isEmpty())) {
            output.put(fieldJsonPath, SET);
          }
        }
      }
    }

    return output;
  }

  private Map<String, Object> generateSyncMetadata(UUID connectionId) throws ConfigNotFoundException, IOException, JsonValidationException {
    final Map<String, Object> operationUsage = new HashMap<>();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);
    for (UUID operationId : standardSync.getOperationIds()) {
      StandardSyncOperation operation = configRepository.getStandardSyncOperation(operationId);
      if (operation != null) {
        final Integer usageCount = (Integer) operationUsage.getOrDefault(OPERATION + operation.getOperatorType(), 0);
        operationUsage.put(OPERATION + operation.getOperatorType(), usageCount + 1);
      }
    }
    return MoreMaps.merge(TrackingMetadata.generateSyncMetadata(standardSync), operationUsage);
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
    final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    return TrackingMetadata.generateDestinationDefinitionMetadata(destinationDefinition);
  }

  private ImmutableMap<String, Object> generateSourceDefinitionMetadata(UUID sourceDefinitionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    return TrackingMetadata.generateSourceDefinitionMetadata(sourceDefinition);
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
    final Job job = jobPersistence.getJob(jobId);
    if (jobState != JobState.STARTED) {
      return TrackingMetadata.generateJobAttemptMetadata(job);
    } else {
      return ImmutableMap.of();
    }
  }

  private void track(UUID workspaceId, Map<String, Object> metadata) {
    // unfortunate but in the case of jobs that cannot be linked to a workspace there not a sensible way
    // track it.
    if (workspaceId != null) {
      trackingClient.track(workspaceId, MESSAGE_NAME, metadata);
    }
  }

}
