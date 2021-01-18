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

import io.airbyte.config.AirbyteProtocolConverters;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.Optional;

public class DefaultJobCreator implements JobCreator {

  private final JobPersistence jobPersistence;

  public DefaultJobCreator(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  @Override
  public long createSourceCheckConnectionJob(SourceConnection source, String dockerImageName) throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.CHECK_CONNECTION_SOURCE)
        .withCheckConnection(jobCheckConnectionConfig);

    final String sourceId = source.getSourceId() != null ? source.getSourceId().toString() : "";
    return jobPersistence.enqueueJob(sourceId, jobConfig).orElseThrow();
  }

  @Override
  public long createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImageName) throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destination.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.CHECK_CONNECTION_DESTINATION)
        .withCheckConnection(jobCheckConnectionConfig);

    final String destinationId = destination.getDestinationId() != null ? destination.getDestinationId().toString() : "";
    return jobPersistence.enqueueJob(destinationId, jobConfig).orElseThrow();
  }

  @Override
  public long createDiscoverSchemaJob(SourceConnection source, String dockerImageName) throws IOException {
    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.DISCOVER_SCHEMA)
        .withDiscoverCatalog(jobDiscoverCatalogConfig);

    final String sourceId = source.getSourceId() != null ? source.getSourceId().toString() : "";
    return jobPersistence.enqueueJob(sourceId, jobConfig).orElseThrow();
  }

  @Override
  public long createGetSpecJob(String integrationImage) throws IOException {
    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.GET_SPEC)
        .withGetSpec(new JobGetSpecConfig().withDockerImage(integrationImage));

    return jobPersistence.enqueueJob(integrationImage, jobConfig).orElseThrow();
  }

  @Override
  public Optional<Long> createSyncJob(SourceConnection source,
                                      DestinationConnection destination,
                                      StandardSync standardSync,
                                      String sourceDockerImageName,
                                      String destinationDockerImageName)
      throws IOException {
    // reusing this isn't going to quite work.
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceDockerImage(sourceDockerImageName)
        .withSourceConfiguration(source.getConfiguration())
        .withDestinationDockerImage(destinationDockerImageName)
        .withDestinationConfiguration(destination.getConfiguration())
        .withConfiguredAirbyteCatalog(AirbyteProtocolConverters.toConfiguredCatalog(standardSync.getSchema()))
        .withState(null);

    jobPersistence.getCurrentState(standardSync.getConnectionId()).ifPresent(jobSyncConfig::withState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.SYNC)
        .withSync(jobSyncConfig);
    return jobPersistence.enqueueJob(standardSync.getConnectionId().toString(), jobConfig);
  }

  // Strategy:
  // 1. Set all streams to full refresh.
  // 2. Create a job where the source emits no records.
  // 3. Run a sync from the empty source to the destination. This will overwrite all data for each
  // stream in the destination.
  // 4. The Empty source emits no state message, so state will start at null (i.e. start from the
  // beginning on the next sync).
  @Override
  public Optional<Long> createResetConnectionJob(DestinationConnection destination, StandardSync standardSync, String destinationDockerImage)
      throws IOException {
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = AirbyteProtocolConverters.toConfiguredCatalog(standardSync.getSchema());
    configuredAirbyteCatalog.getStreams().forEach(configuredAirbyteStream -> configuredAirbyteStream.setSyncMode(SyncMode.FULL_REFRESH));

    final JobResetConnectionConfig resetConnectionConfig = new JobResetConnectionConfig()
        .withDestinationDockerImage(destinationDockerImage)
        .withDestinationConfiguration(destination.getConfiguration())
        .withConfiguredAirbyteCatalog(configuredAirbyteCatalog);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(resetConnectionConfig);
    return jobPersistence.enqueueJob(standardSync.getConnectionId().toString(), jobConfig);
  }

}
