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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.JobStatusRead;
import io.airbyte.api.model.JobStatusReadStatus;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobOutput;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.cache.SpecCache;
import io.airbyte.server.cache.SpecCache.AlwaysMissCache;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceHelpers;
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
  private JobPersistence jobPersistence;
  private JobCreator jobCreator;
  private Job inProgressJob;
  private Job completedJob;
  private SpecCache specCache;

  @BeforeEach
  void setup() {
    inProgressJob = mock(Job.class);
    when(inProgressJob.getStatus()).thenReturn(JobStatus.RUNNING);
    completedJob = mock(Job.class);
    when(completedJob.getStatus()).thenReturn(JobStatus.SUCCEEDED);
    specCache = spy(new AlwaysMissCache());

    configRepository = mock(ConfigRepository.class);
    jobPersistence = mock(JobPersistence.class);
    jobCreator = mock(JobCreator.class);
    schedulerHandler = new SchedulerHandler(configRepository, jobPersistence, jobCreator, specCache);
  }

  @Test
  void testCheckSourceConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceIdRequestBody request = new SourceIdRequestBody().sourceId(source.getSourceId());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(jobCreator.createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    schedulerHandler.checkSourceConnection(request);

    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(jobCreator).createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE);
    verify(jobPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testGetSourceSpec() throws JsonValidationException, IOException, ConfigNotFoundException, URISyntaxException {
    final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody = new SourceDefinitionIdRequestBody().sourceDefinitionId(UUID.randomUUID());
    when(configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withName("name")
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(sourceDefinitionIdRequestBody.getSourceDefinitionId()));
    when(jobCreator.createGetSpecJob(SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    final StandardGetSpecOutput specOutput = new StandardGetSpecOutput().withSpecification(
        new ConnectorSpecification()
            .withDocumentationUrl(new URI("https://google.com"))
            .withChangelogUrl(new URI("https://google.com"))
            .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));
    final JobOutput jobOutput = mock(JobOutput.class);

    when(jobOutput.getGetSpec()).thenReturn(specOutput);
    when(completedJob.getSuccessOutput()).thenReturn(Optional.of(jobOutput));

    schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody);

    verify(configRepository).getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    verify(jobCreator).createGetSpecJob(SOURCE_DOCKER_IMAGE);
    verify(jobPersistence, atLeast(2)).getJob(JOB_ID);
  }

  @Test
  void testGetDestinationSpec() throws JsonValidationException, IOException, ConfigNotFoundException, URISyntaxException {
    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody =
        new DestinationDefinitionIdRequestBody().destinationDefinitionId(UUID.randomUUID());

    when(configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withName("name")
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destinationDefinitionIdRequestBody.getDestinationDefinitionId()));
    when(jobCreator.createGetSpecJob(DESTINATION_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    final StandardGetSpecOutput specOutput = new StandardGetSpecOutput().withSpecification(
        new ConnectorSpecification()
            .withDocumentationUrl(new URI("https://google.com"))
            .withChangelogUrl(new URI("https://google.com"))
            .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));
    final JobOutput jobOutput = mock(JobOutput.class);
    when(jobOutput.getGetSpec()).thenReturn(specOutput);
    when(completedJob.getSuccessOutput()).thenReturn(Optional.of(jobOutput));

    schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody);

    verify(configRepository).getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    verify(jobCreator).createGetSpecJob(DESTINATION_DOCKER_IMAGE);
    verify(jobPersistence, atLeast(2)).getJob(JOB_ID);
  }

  @Test
  public void testGetConnectorSpec() throws IOException, URISyntaxException {
    when(jobCreator.createGetSpecJob(SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);
    final StandardGetSpecOutput specOutput = new StandardGetSpecOutput().withSpecification(
        new ConnectorSpecification()
            .withDocumentationUrl(new URI("https://google.com"))
            .withChangelogUrl(new URI("https://google.com"))
            .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));
    final JobOutput jobOutput = mock(JobOutput.class);
    when(jobOutput.getGetSpec()).thenReturn(specOutput);
    when(completedJob.getSuccessOutput()).thenReturn(Optional.of(jobOutput));

    assertEquals(specOutput.getSpecification(), schedulerHandler.getConnectorSpecification(SOURCE_DOCKER_IMAGE));

    verify(jobCreator).createGetSpecJob(SOURCE_DOCKER_IMAGE);
    verify(jobPersistence, atLeast(2)).getJob(JOB_ID);
    verify(specCache).get(SOURCE_DOCKER_IMAGE);
    verify(specCache).put(SOURCE_DOCKER_IMAGE, specOutput.getSpecification());
  }

  @Test
  public void testGetConnectorSpecCached() throws IOException, URISyntaxException {
    final ConnectorSpecification spec = new ConnectorSpecification()
        .withDocumentationUrl(new URI("https://google.com"))
        .withChangelogUrl(new URI("https://google.com"))
        .withConnectionSpecification(Jsons.jsonNode(new HashMap<>()));
    when(specCache.get(SOURCE_DOCKER_IMAGE)).thenReturn(Optional.of(spec));

    assertEquals(spec, schedulerHandler.getConnectorSpecification(SOURCE_DOCKER_IMAGE));

    // whole point of caching is to not need to schedule a job.
    verifyNoInteractions(jobPersistence);
    verify(specCache).get(SOURCE_DOCKER_IMAGE);
    verifyNoMoreInteractions(specCache);
  }

  @Test
  void testCheckDestinationConnection() throws IOException, JsonValidationException, ConfigNotFoundException {
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    final DestinationIdRequestBody request = new DestinationIdRequestBody().destinationId(destination.getDestinationId());

    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destination.getDestinationDefinitionId()));
    when(configRepository.getDestinationConnection(destination.getDestinationId())).thenReturn(destination);
    when(jobCreator.createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    schedulerHandler.checkDestinationConnection(request);

    verify(configRepository).getDestinationConnection(destination.getDestinationId());
    verify(jobCreator).createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE);
    verify(jobPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testDiscoverSchemaForSource() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceIdRequestBody request = new SourceIdRequestBody().sourceId(source.getSourceId());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(jobCreator.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE)).thenReturn(JOB_ID);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    schedulerHandler.discoverSchemaForSource(request);

    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(jobCreator).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
    verify(jobPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testSyncConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(UUID.randomUUID());
    final ConnectionIdRequestBody request = new ConnectionIdRequestBody().connectionId(standardSync.getConnectionId());
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID()).withSourceId(standardSync.getSourceId());
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID())
        .withDestinationId(standardSync.getDestinationId());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destination.getDestinationDefinitionId()));
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(configRepository.getDestinationConnection(destination.getDestinationId())).thenReturn(destination);
    when(jobCreator.createSyncJob(source, destination, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE))
        .thenReturn(JOB_ID);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(inProgressJob).thenReturn(completedJob);

    final JobStatusRead jobStatusRead = schedulerHandler.syncConnection(request);

    assertEquals(JobStatusReadStatus.SUCCEEDED, jobStatusRead.getStatus());
    verify(configRepository).getStandardSync(standardSync.getConnectionId());
    verify(configRepository).getSourceConnection(standardSync.getSourceId());
    verify(configRepository).getDestinationConnection(standardSync.getDestinationId());
    verify(jobCreator).createSyncJob(source, destination, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE);
    verify(jobPersistence, times(2)).getJob(JOB_ID);
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(StandardCheckConnectionOutput.Status.class, CheckConnectionRead.StatusEnum.class));
  }

}
