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
import io.airbyte.scheduler.client.SynchronousJobResponse.SynchronousJobMetadata;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalJobException;
import java.io.IOException;
import java.time.Instant;
import java.util.UUID;

public class DefaultSynchronousSchedulerJobClient implements SynchronousSchedulerJobClient {

  private final TemporalClient temporalClient;

  public DefaultSynchronousSchedulerJobClient(TemporalClient temporalClient) {
    this.temporalClient = temporalClient;
  }

  @Override
  public SynchronousJobResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(final SourceConnection source, final String dockerImage)
      throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_SOURCE,
        source.getSourceId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig));
  }

  @Override
  public SynchronousJobResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(final DestinationConnection destination,
                                                                                                   final String dockerImage)
      throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destination.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_DESTINATION,
        destination.getDestinationId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig));
  }

  @Override
  public SynchronousJobResponse<AirbyteCatalog> createDiscoverSchemaJob(final SourceConnection source, final String dockerImage) throws IOException {
    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.DISCOVER_SCHEMA,
        source.getSourceId(),
        jobId -> temporalClient.submitDiscoverSchema(UUID.randomUUID(), 0, jobDiscoverCatalogConfig));
  }

  @Override
  public SynchronousJobResponse<ConnectorSpecification> createGetSpecJob(final String dockerImage) throws IOException {
    final JobGetSpecConfig jobSpecConfig = new JobGetSpecConfig().withDockerImage(dockerImage);

    return execute(
        ConfigType.GET_SPEC,
        null,
        jobId -> temporalClient.submitGetSpec(UUID.randomUUID(), 0, jobSpecConfig));
  }

  // config id can be empty
  private static <T> SynchronousJobResponse<T> execute(ConfigType configType,
                                                       UUID configId,
                                                       CheckedFunction<UUID, T, TemporalJobException> executor) {
    final long createdAt = Instant.now().toEpochMilli();
    T value = null;
    TemporalJobException exception = null;
    final UUID jobId = UUID.randomUUID();
    try {
      value = executor.apply(jobId);
    } catch (TemporalJobException e) {
      exception = e;
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

    return new SynchronousJobResponse<>(value, metadata);
  }

}
