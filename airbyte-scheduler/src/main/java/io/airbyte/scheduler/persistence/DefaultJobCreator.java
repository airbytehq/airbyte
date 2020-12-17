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
import io.airbyte.scheduler.ScopeHelper;
import java.io.IOException;

public class DefaultJobCreator implements JobCreator {

  private final JobPersistence jobPersistence;

  public DefaultJobCreator(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  @Override
  public long createSourceCheckConnectionJob(SourceConnection source, String dockerImageName) throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_SOURCE,
            source.getSourceId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE)
        .withCheckConnection(jobCheckConnectionConfig);

    return jobPersistence.createJob(scope, jobConfig);
  }

  @Override
  public long createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImageName) throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION,
            destination.getDestinationId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destination.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION)
        .withCheckConnection(jobCheckConnectionConfig);

    return jobPersistence.createJob(scope, jobConfig);
  }

  @Override
  public long createDiscoverSchemaJob(SourceConnection source, String dockerImageName) throws IOException {
    final String scope = ScopeHelper.createScope(
        JobConfig.ConfigType.DISCOVER_SCHEMA,
        source.getSourceId().toString());

    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA)
        .withDiscoverCatalog(jobDiscoverCatalogConfig);

    return jobPersistence.createJob(scope, jobConfig);
  }

  @Override
  public long createGetSpecJob(String integrationImage) throws IOException {
    final String scope = ScopeHelper.createScope(
        JobConfig.ConfigType.GET_SPEC,
        integrationImage);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.GET_SPEC)
        .withGetSpec(new JobGetSpecConfig().withDockerImage(integrationImage));

    return jobPersistence.createJob(scope, jobConfig);
  }

  @Override
  public long createSyncJob(SourceConnection source,
                            DestinationConnection destination,
                            StandardSync standardSync,
                            String sourceDockerImageName,
                            String destinationDockerImageName)
      throws IOException {
    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, standardSync.getConnectionId().toString());

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
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);
    return jobPersistence.createJob(scope, jobConfig);
  }

  // Strategy:
  // 1. Set all streams to full refresh.
  // 2. Create a job where the source emits no records.
  // 3. Run a sync from the empty source to the destination. This will overwrite all data for each
  // stream in the destination.
  // 4. The Empty source emits no state message, so state will start at null (i.e. start from the
  // beginning on the next sync).
  @Override
  public long createResetConnectionJob(DestinationConnection destination, StandardSync standardSync, String destinationDockerImage)
      throws IOException {
    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, standardSync.getConnectionId().toString());

    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = AirbyteProtocolConverters.toConfiguredCatalog(standardSync.getSchema());
    configuredAirbyteCatalog.getStreams().forEach(configuredAirbyteStream -> configuredAirbyteStream.setSyncMode(SyncMode.FULL_REFRESH));

    final JobResetConnectionConfig resetConnectionConfig = new JobResetConnectionConfig()
        .withDestinationDockerImage(destinationDockerImage)
        .withDestinationConfiguration(destination.getConfiguration())
        .withConfiguredAirbyteCatalog(configuredAirbyteCatalog);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(resetConnectionConfig);
    return jobPersistence.createJob(scope, jobConfig);
  }

}
