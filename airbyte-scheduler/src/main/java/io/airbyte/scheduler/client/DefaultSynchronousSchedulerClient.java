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
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.JobTracker;
import io.airbyte.scheduler.JobTracker.JobState;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalJobException;
import java.io.IOException;
import java.time.Instant;
import java.util.UUID;

public class DefaultSynchronousSchedulerClient implements SynchronousSchedulerClient {

  private final TemporalClient temporalClient;
  private final JobTracker jobTracker;

  public DefaultSynchronousSchedulerClient(TemporalClient temporalClient, JobTracker jobTracker) {
    this.temporalClient = temporalClient;
    this.jobTracker = jobTracker;
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(final SourceConnection source, final String dockerImage)
      throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_SOURCE,
        source.getSourceId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig),
        source.getSourceDefinitionId());
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(final DestinationConnection destination,
                                                                                                final String dockerImage)
      throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destination.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_DESTINATION,
        destination.getDestinationId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig),
        destination.getDestinationDefinitionId());
  }

  @Override
  public SynchronousResponse<AirbyteCatalog> createDiscoverSchemaJob(final SourceConnection source, final String dockerImage) throws IOException {
    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.DISCOVER_SCHEMA,
        source.getSourceId(),
        jobId -> temporalClient.submitDiscoverSchema(UUID.randomUUID(), 0, jobDiscoverCatalogConfig),
        source.getSourceDefinitionId());
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

  // config id can be empty
  @VisibleForTesting
  <T> SynchronousResponse<T> execute(ConfigType configType,
                                     UUID configId,
                                     CheckedFunction<UUID, T, TemporalJobException> executor,
                                     UUID jobTrackerId) {
    final long createdAt = Instant.now().toEpochMilli();
    T operationOutput = null;
    TemporalJobException exception = null;
    final UUID jobId = UUID.randomUUID();
    try {
      track(jobId, configType, jobTrackerId, JobState.STARTED, null);
      operationOutput = executor.apply(jobId);
      track(jobId, configType, jobTrackerId, JobState.SUCCEEDED, operationOutput);
    } catch (TemporalJobException e) {
      exception = e;
      track(jobId, configType, jobTrackerId, JobState.FAILED, operationOutput);
    } catch (Exception e) {
      track(jobId, configType, jobTrackerId, JobState.FAILED, operationOutput);
      throw e;
    }
    final long endedAt = Instant.now().toEpochMilli();

    final SynchronousJobMetadata metadata = new SynchronousJobMetadata(
        jobId,
        configType,
        configId,
        createdAt,
        endedAt,
        exception == null,
        exception != null ? exception.getLogPath() : null);

    return new SynchronousResponse<>(operationOutput, metadata);
  }

  private <T> void track(UUID jobId, ConfigType configType, UUID jobTrackerId, JobState jobState, T value) {
    switch (configType) {
      case CHECK_CONNECTION_SOURCE -> jobTracker.trackCheckConnectionSource(jobId, jobTrackerId, jobState, (StandardCheckConnectionOutput) value);
      case CHECK_CONNECTION_DESTINATION -> jobTracker.trackCheckConnectionDestination(jobId, jobTrackerId, jobState,
          (StandardCheckConnectionOutput) value);
      case DISCOVER_SCHEMA -> jobTracker.trackDiscover(jobId, jobTrackerId, jobState);
      case GET_SPEC -> {
        // skip tracking for get spec to avoid noise.
      }
      default -> throw new IllegalArgumentException(
          String.format("Jobs of type %s cannot be processed here. They should be consumed in the JobSubmitter.", configType));
    }

  }

}
