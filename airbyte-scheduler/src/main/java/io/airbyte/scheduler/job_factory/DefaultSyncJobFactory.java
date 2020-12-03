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

package io.airbyte.scheduler.job_factory;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.DefaultJobCreator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;

public class DefaultSyncJobFactory implements SyncJobFactory {

  private final DefaultJobCreator jobCreator;
  private final ConfigRepository configRepository;

  public DefaultSyncJobFactory(final DefaultJobCreator jobCreator,
                               final ConfigRepository configRepository) {

    this.jobCreator = jobCreator;
    this.configRepository = configRepository;
  }

  public Long create(final UUID connectionId) {
    try {
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);
      final SourceConnection sourceConnection =
          configRepository.getSourceConnection(standardSync.getSourceId());
      final DestinationConnection destinationConnection =
          configRepository.getDestinationConnection(standardSync.getDestinationId());

      final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
      final StandardDestinationDefinition destinationDefinition =
          configRepository.getStandardDestinationDefinition(destinationConnection.getDestinationDefinitionId());

      final String sourceImageName = DockerUtils.getTaggedImageName(sourceDefinition.getDockerRepository(), sourceDefinition.getDockerImageTag());
      final String destinationImageName =
          DockerUtils.getTaggedImageName(destinationDefinition.getDockerRepository(), destinationDefinition.getDockerImageTag());

      return jobCreator.createSyncJob(
          sourceConnection,
          destinationConnection,
          standardSync,
          sourceImageName,
          destinationImageName);

    } catch (IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

}
