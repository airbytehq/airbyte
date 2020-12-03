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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

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
import org.junit.jupiter.api.Test;

class DefaultSyncJobFactoryTest {

  @Test
  void createSyncJobFromConnectionId() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID destinationDefinitionId = UUID.randomUUID();
    final UUID connectionId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final UUID destinationId = UUID.randomUUID();
    final DefaultJobCreator jobCreator = mock(DefaultJobCreator.class);
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final long jobId = 11L;

    final StandardSync standardSync = new StandardSync()
        .withSourceId(sourceId)
        .withDestinationId(destinationId);

    final SourceConnection sourceConnection = new SourceConnection().withSourceDefinitionId(sourceDefinitionId);
    final DestinationConnection destinationConnection =
        new DestinationConnection().withDestinationDefinitionId(destinationDefinitionId);
    final String srcDockerRepo = "srcrepo";
    final String srcDockerTag = "tag";
    final String srcDockerImage = DockerUtils.getTaggedImageName(srcDockerRepo, srcDockerTag);

    final String dstDockerRepo = "dstrepo";
    final String dstDockerTag = "tag";
    final String dstDockerImage = DockerUtils.getTaggedImageName(dstDockerRepo, dstDockerTag);

    when(configRepository.getStandardSync(connectionId)).thenReturn(standardSync);
    when(configRepository.getSourceConnection(sourceId)).thenReturn(sourceConnection);
    when(configRepository.getDestinationConnection(destinationId)).thenReturn(destinationConnection);
    when(jobCreator
        .createSyncJob(sourceConnection, destinationConnection, standardSync, srcDockerImage, dstDockerImage))
            .thenReturn(jobId);
    when(configRepository.getStandardSourceDefinition(sourceDefinitionId))
        .thenReturn(new StandardSourceDefinition().withSourceDefinitionId(sourceDefinitionId).withDockerRepository(srcDockerRepo)
            .withDockerImageTag(srcDockerTag));

    when(configRepository.getStandardDestinationDefinition(destinationDefinitionId))
        .thenReturn(new StandardDestinationDefinition().withDestinationDefinitionId(destinationDefinitionId).withDockerRepository(dstDockerRepo)
            .withDockerImageTag(dstDockerTag));

    final SyncJobFactory factory = new DefaultSyncJobFactory(jobCreator, configRepository);
    final long actualJobId = factory.create(connectionId);
    assertEquals(jobId, actualJobId);

    verify(jobCreator)
        .createSyncJob(sourceConnection, destinationConnection, standardSync, srcDockerImage, dstDockerImage);
  }

}
