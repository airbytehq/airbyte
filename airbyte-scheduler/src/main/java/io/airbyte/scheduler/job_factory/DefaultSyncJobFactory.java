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

import io.airbyte.commons.docker.DockerUtil;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.StandardSource;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.util.UUID;

public class DefaultSyncJobFactory implements SyncJobFactory {

  private final SchedulerPersistence schedulerPersistence;
  private final ConfigRepository configRepository;

  public DefaultSyncJobFactory(final SchedulerPersistence schedulerPersistence,
                               final ConfigRepository configRepository) {

    this.schedulerPersistence = schedulerPersistence;
    this.configRepository = configRepository;
  }

  public Long create(final UUID connectionId) {
    try {
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);
      final SourceConnectionImplementation sourceConnectionImplementation =
          configRepository.getSourceConnectionImplementation(standardSync.getSourceImplementationId());
      final DestinationConnectionImplementation destinationConnectionImplementation =
          configRepository.getDestinationConnectionImplementation(standardSync.getDestinationImplementationId());

      final StandardSource source = configRepository.getStandardSource(sourceConnectionImplementation.getSourceId());
      final StandardDestination destination = configRepository.getStandardDestination(destinationConnectionImplementation.getDestinationId());

      final String sourceImageName = DockerUtil.getTaggedImageName(source.getDockerRepository(), source.getDockerImageTag());
      final String destinationImageName = DockerUtil.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());

      return schedulerPersistence.createSyncJob(
          sourceConnectionImplementation,
          destinationConnectionImplementation,
          standardSync,
          sourceImageName,
          destinationImageName);

    } catch (IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

}
