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

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationImplementationIdRequestBody;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceImplementationIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.JobOutput;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.config.StandardSource;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.persistence.SchedulerPersistence;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationImplementationHelpers;
import io.airbyte.server.helpers.SourceImplementationHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SchedulerHandlerTest {

  private static final long JOB_ID = 15L;

  private static final String SOURCE_DOCKER_REPO = "srcimage";
  private static final String SOURCE_DOCKER_TAG = "tag";
  private static final String SOURCE_DOCKER_IMAGE = DockerUtils.getTaggedImageName(SOURCE_DOCKER_REPO, SOURCE_DOCKER_TAG);

  private static final String DESTINATION_DOCKER_REPO = "dstimage";
  private static final String DESTINATION_DOCKER_TAG = "tag";
  private static final String DESTINATION_DOCKER_IMAGE = DockerUtils.getTaggedImageName(DESTINATION_DOCKER_REPO, DESTINATION_DOCKER_TAG);

  private SchedulerHandler schedulerHandler;
  private ConfigRepository configRepository;
  private SchedulerPersistence schedulerPersistence;
  private Job inProgressJob;
  private Job completedJob;

  @BeforeEach
  void setup() {
    inProgressJob = mock(Job.class);
    when(inProgressJob.getStatus()).thenReturn(JobStatus.RUNNING);
    completedJob = mock(Job.class);
    when(completedJob.getStatus()).thenReturn(JobStatus.COMPLETED);

    configRepository = mock(ConfigRepository.class);
    schedulerPersistence = mock(SchedulerPersistence.class);
    schedulerHandler = new SchedulerHandler(configRepository, schedulerPersistence);
  }

  @Test
  void testCheckSourceImplementationConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    SourceConnectionImplementation sourceImpl = SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID());
    final SourceImplementationIdRequestBody request =
        new SourceImplementationIdRequestBody().sourceImplementationId(sourceImpl.getSourceImplementationId());

    when(configRepository.getStandardSource(sourceImpl.getSourceId()))
        .thenReturn(new StandardSource()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceId(sourceImpl.getSourceId()));
    when(configRepository.getSourceConnectionImplementation(sourceImpl.getSourceImplementationId())).thenReturn(sourceImpl);
    when(schedulerPersistence.createSourceCheckConnectionJob(sourceImpl, SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    schedulerHandler.checkSourceImplementationConnection(request);

    verify(configRepository).getSourceConnectionImplementation(sourceImpl.getSourceImplementationId());
    verify(schedulerPersistence).createSourceCheckConnectionJob(sourceImpl, SOURCE_DOCKER_IMAGE);
    verify(schedulerPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testGetSourceSpec() throws JsonValidationException, IOException, ConfigNotFoundException, URISyntaxException {
    SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(UUID.randomUUID());
    when(configRepository.getStandardSource(sourceIdRequestBody.getSourceId()))
        .thenReturn(new StandardSource()
            .withName("name")
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceId(sourceIdRequestBody.getSourceId()));
    when(schedulerPersistence.createGetSpecJob(SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    StandardGetSpecOutput specOutput = new StandardGetSpecOutput().withSpecification(
        new ConnectorSpecification()
            .withDocumentationUrl(new URI("https://google.com"))
            .withChangelogUrl(new URI("https://google.com"))
            .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));
    JobOutput jobOutput = mock(JobOutput.class);

    when(jobOutput.getGetSpec()).thenReturn(specOutput);
    when(completedJob.getOutput()).thenReturn(Optional.of(jobOutput));

    schedulerHandler.getSourceSpecification(sourceIdRequestBody);

    verify(configRepository).getStandardSource(sourceIdRequestBody.getSourceId());
    verify(schedulerPersistence).createGetSpecJob(SOURCE_DOCKER_IMAGE);
    verify(schedulerPersistence, atLeast(2)).getJob(JOB_ID);
  }

  @Test
  void testGetDestinationSpec() throws JsonValidationException, IOException, ConfigNotFoundException, URISyntaxException {
    DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(UUID.randomUUID());

    when(configRepository.getStandardDestination(destinationIdRequestBody.getDestinationId()))
        .thenReturn(new StandardDestination()
            .withName("name")
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationId(destinationIdRequestBody.getDestinationId()));
    when(schedulerPersistence.createGetSpecJob(DESTINATION_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    StandardGetSpecOutput specOutput = new StandardGetSpecOutput().withSpecification(
        new ConnectorSpecification()
            .withDocumentationUrl(new URI("https://google.com"))
            .withChangelogUrl(new URI("https://google.com"))
            .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));
    JobOutput jobOutput = mock(JobOutput.class);
    when(jobOutput.getGetSpec()).thenReturn(specOutput);
    when(completedJob.getOutput()).thenReturn(Optional.of(jobOutput));

    schedulerHandler.getDestinationSpecification(destinationIdRequestBody);

    verify(configRepository).getStandardDestination(destinationIdRequestBody.getDestinationId());
    verify(schedulerPersistence).createGetSpecJob(DESTINATION_DOCKER_IMAGE);
    verify(schedulerPersistence, atLeast(2)).getJob(JOB_ID);
  }

  @Test
  public void testGetConnectorSpec() throws IOException, URISyntaxException {
    when(schedulerPersistence.createGetSpecJob(SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);
    StandardGetSpecOutput specOutput = new StandardGetSpecOutput().withSpecification(
        new ConnectorSpecification()
            .withDocumentationUrl(new URI("https://google.com"))
            .withChangelogUrl(new URI("https://google.com"))
            .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));
    JobOutput jobOutput = mock(JobOutput.class);
    when(jobOutput.getGetSpec()).thenReturn(specOutput);
    when(completedJob.getOutput()).thenReturn(Optional.of(jobOutput));

    schedulerHandler.getConnectorSpecification(SOURCE_DOCKER_IMAGE);

    verify(schedulerPersistence).createGetSpecJob(SOURCE_DOCKER_IMAGE);
    verify(schedulerPersistence, atLeast(2)).getJob(JOB_ID);
  }

  @Test
  void testCheckDestinationImplementationConnection() throws IOException, JsonValidationException, ConfigNotFoundException {
    DestinationConnectionImplementation destinationImpl = DestinationImplementationHelpers.generateDestinationImplementation(UUID.randomUUID());
    final DestinationImplementationIdRequestBody request =
        new DestinationImplementationIdRequestBody().destinationImplementationId(destinationImpl.getDestinationImplementationId());

    when(configRepository.getStandardDestination(destinationImpl.getDestinationId()))
        .thenReturn(new StandardDestination()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationId(destinationImpl.getDestinationId()));
    when(configRepository.getDestinationConnectionImplementation(destinationImpl.getDestinationImplementationId())).thenReturn(destinationImpl);
    when(schedulerPersistence.createDestinationCheckConnectionJob(destinationImpl, DESTINATION_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    schedulerHandler.checkDestinationImplementationConnection(request);

    verify(configRepository).getDestinationConnectionImplementation(destinationImpl.getDestinationImplementationId());
    verify(schedulerPersistence).createDestinationCheckConnectionJob(destinationImpl, DESTINATION_DOCKER_IMAGE);
    verify(schedulerPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testDiscoverSchemaForSourceImplementation() throws IOException, JsonValidationException, ConfigNotFoundException {
    SourceConnectionImplementation sourceImpl = SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID());
    final SourceImplementationIdRequestBody request =
        new SourceImplementationIdRequestBody().sourceImplementationId(sourceImpl.getSourceImplementationId());

    when(configRepository.getStandardSource(sourceImpl.getSourceId()))
        .thenReturn(new StandardSource()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceId(sourceImpl.getSourceId()));
    when(configRepository.getSourceConnectionImplementation(sourceImpl.getSourceImplementationId())).thenReturn(sourceImpl);
    when(schedulerPersistence.createDiscoverSchemaJob(sourceImpl, SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    schedulerHandler.discoverSchemaForSourceImplementation(request);

    verify(configRepository).getSourceConnectionImplementation(sourceImpl.getSourceImplementationId());
    verify(schedulerPersistence).createDiscoverSchemaJob(sourceImpl, SOURCE_DOCKER_IMAGE);
    verify(schedulerPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testSyncConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceImplId(UUID.randomUUID());
    final ConnectionIdRequestBody request = new ConnectionIdRequestBody().connectionId(standardSync.getConnectionId());
    SourceConnectionImplementation sourceImpl = SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID())
        .withSourceImplementationId(standardSync.getSourceImplementationId());
    DestinationConnectionImplementation destinationImpl = DestinationImplementationHelpers.generateDestinationImplementation(UUID.randomUUID())
        .withDestinationImplementationId(standardSync.getDestinationImplementationId());

    when(configRepository.getStandardSource(sourceImpl.getSourceId()))
        .thenReturn(new StandardSource()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceId(sourceImpl.getSourceId()));
    when(configRepository.getStandardDestination(destinationImpl.getDestinationId()))
        .thenReturn(new StandardDestination()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationId(destinationImpl.getDestinationId()));
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
    when(configRepository.getSourceConnectionImplementation(sourceImpl.getSourceImplementationId())).thenReturn(sourceImpl);
    when(configRepository.getDestinationConnectionImplementation(destinationImpl.getDestinationImplementationId())).thenReturn(destinationImpl);
    when(schedulerPersistence.createSyncJob(sourceImpl, destinationImpl, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE))
        .thenReturn(JOB_ID);
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    schedulerHandler.syncConnection(request);

    verify(configRepository).getStandardSync(standardSync.getConnectionId());
    verify(configRepository).getSourceConnectionImplementation(standardSync.getSourceImplementationId());
    verify(configRepository).getDestinationConnectionImplementation(standardSync.getDestinationImplementationId());
    verify(schedulerPersistence).createSyncJob(sourceImpl, destinationImpl, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE);
    verify(schedulerPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(StandardCheckConnectionOutput.Status.class, CheckConnectionRead.StatusEnum.class));
  }

}
