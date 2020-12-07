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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteProtocolConverters;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.AttemptStatus;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.ScopeHelper;
import java.io.IOException;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public class DefaultJobCreator implements JobCreator {

  private JobPersistence jobPersistence;

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
    return createSyncJobInternal(
        standardSync.getConnectionId(),
        source.getConfiguration(),
        destination.getConfiguration(),
        AirbyteProtocolConverters.toConfiguredCatalog(standardSync.getSchema()),
        sourceDockerImageName,
        destinationDockerImageName);
  }

  private long createSyncJobInternal(
                                     UUID connectionId,
                                     JsonNode sourceConfiguration,
                                     JsonNode destinationConfiguration,
                                     ConfiguredAirbyteCatalog configuredAirbyteCatalog,
                                     String sourceDockerImageName,
                                     String destinationDockerImageName)
      throws IOException {
    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString());

    // reusing this isn't going to quite work.
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceDockerImage(sourceDockerImageName)
        .withSourceConfiguration(sourceConfiguration)
        .withDestinationDockerImage(destinationDockerImageName)
        .withDestinationConfiguration(destinationConfiguration)
        .withConfiguredAirbyteCatalog(configuredAirbyteCatalog)
        .withState(null);

    // todo (cgardens) - this will not have the intended behavior if the last job failed. then the next
    // job will assume there is no state and re-sync everything! this is already wrong, so i'm not going
    // to increase the scope of the current project.
    final Optional<Job> previousJobOptional = jobPersistence.getLastSyncJob(connectionId);

    final Optional<State> stateOptional = previousJobOptional.flatMap(j -> {
      final List<Attempt> attempts = j.getAttempts() != null ? j.getAttempts() : Lists.newArrayList();
      // find oldest attempt that is either succeeded or contains state.
      return attempts.stream()
          .filter(
              a -> a.getStatus() == AttemptStatus.SUCCEEDED || a.getOutput().map(JobOutput::getSync).map(StandardSyncOutput::getState).isPresent())
          .max(Comparator.comparingLong(Attempt::getCreatedAtInSecond))
          .map(Attempt::getOutput)
          .map(Optional::get)
          .map(JobOutput::getSync)
          .map(StandardSyncOutput::getState);
    });
    stateOptional.ifPresent(jobSyncConfig::withState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);
    return jobPersistence.createJob(scope, jobConfig);
  }

}
