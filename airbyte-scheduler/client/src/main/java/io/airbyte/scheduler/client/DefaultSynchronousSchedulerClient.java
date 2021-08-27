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

package io.airbyte.scheduler.client;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalResponse;
import java.io.IOException;
import java.time.Instant;
import java.util.UUID;
import java.util.function.Function;
import javax.annotation.Nullable;

public class DefaultSynchronousSchedulerClient implements SynchronousSchedulerClient {

  private final TemporalClient temporalClient;
  private final JobTracker jobTracker;

  public DefaultSynchronousSchedulerClient(TemporalClient temporalClient, JobTracker jobTracker) {
    this.temporalClient = temporalClient;
    this.jobTracker = jobTracker;
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(final SourceConnection source, final String dockerImage) {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_SOURCE,
        source.getSourceDefinitionId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig),
        source.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(final DestinationConnection destination,
                                                                                                final String dockerImage) {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destination.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_DESTINATION,
        destination.getDestinationDefinitionId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig),
        destination.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<AirbyteCatalog> createDiscoverSchemaJob(final SourceConnection source, final String dockerImage) {
    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.DISCOVER_SCHEMA,
        source.getSourceDefinitionId(),
        jobId -> temporalClient.submitDiscoverSchema(UUID.randomUUID(), 0, jobDiscoverCatalogConfig),
        source.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<ConnectorSpecification> createGetSpecJob(final String dockerImage) throws IOException {
    final JobGetSpecConfig jobSpecConfig = new JobGetSpecConfig().withDockerImage(dockerImage);

    return execute(
        ConfigType.GET_SPEC,
        null,
        jobId -> temporalClient.submitGetSpec(UUID.randomUUID(), 0, jobSpecConfig),
        null);
  }

  @VisibleForTesting
  <T> SynchronousResponse<T> execute(ConfigType configType,
                                     @Nullable UUID connectorDefinitionId,
                                     Function<UUID, TemporalResponse<T>> executor,
                                     UUID workspaceId) {
    final long createdAt = Instant.now().toEpochMilli();
    final UUID jobId = UUID.randomUUID();
    try {
      track(jobId, configType, connectorDefinitionId, workspaceId, JobState.STARTED, null);
      final TemporalResponse<T> operationOutput = executor.apply(jobId);
      JobState outputState = operationOutput.getMetadata().isSucceeded() ? JobState.SUCCEEDED : JobState.FAILED;
      track(jobId, configType, connectorDefinitionId, workspaceId, outputState, operationOutput.getOutput().orElse(null));
      final long endedAt = Instant.now().toEpochMilli();

      return SynchronousResponse.fromTemporalResponse(
          operationOutput,
          jobId,
          configType,
          connectorDefinitionId,
          createdAt,
          endedAt);
    } catch (RuntimeException e) {
      track(jobId, configType, connectorDefinitionId, workspaceId, JobState.FAILED, null);
      throw e;
    }
  }

  /**
   * @param connectorDefinitionId either source or destination definition id
   */
  private <T> void track(UUID jobId, ConfigType configType, UUID connectorDefinitionId, UUID workspaceId, JobState jobState, T value) {
    switch (configType) {
      case CHECK_CONNECTION_SOURCE -> jobTracker.trackCheckConnectionSource(
          jobId,
          connectorDefinitionId,
          workspaceId,
          jobState,
          (StandardCheckConnectionOutput) value);
      case CHECK_CONNECTION_DESTINATION -> jobTracker.trackCheckConnectionDestination(
          jobId,
          connectorDefinitionId,
          workspaceId,
          jobState,
          (StandardCheckConnectionOutput) value);
      case DISCOVER_SCHEMA -> jobTracker.trackDiscover(jobId, connectorDefinitionId, workspaceId, jobState);
      case GET_SPEC -> {
        // skip tracking for get spec to avoid noise.
      }
      default -> throw new IllegalArgumentException(
          String.format("Jobs of type %s cannot be processed here. They should be consumed in the JobSubmitter.", configType));
    }

  }

}
