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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.client.SchedulerJobClient;
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

  private static final String SOURCE_DOCKER_REPO = "srcimage";
  private static final String SOURCE_DOCKER_TAG = "tag";
  private static final String SOURCE_DOCKER_IMAGE = DockerUtils.getTaggedImageName(SOURCE_DOCKER_REPO, SOURCE_DOCKER_TAG);

  private static final String DESTINATION_DOCKER_REPO = "dstimage";
  private static final String DESTINATION_DOCKER_TAG = "tag";
  private static final String DESTINATION_DOCKER_IMAGE = DockerUtils.getTaggedImageName(DESTINATION_DOCKER_REPO, DESTINATION_DOCKER_TAG);

  private SchedulerHandler schedulerHandler;
  private ConfigRepository configRepository;
  private Job completedJob;
  private SchedulerJobClient schedulerJobClient;

  @BeforeEach
  void setup() {
    completedJob = mock(Job.class);
    when(completedJob.getStatus()).thenReturn(JobStatus.SUCCEEDED);
    schedulerJobClient = spy(SchedulerJobClient.class);

    configRepository = mock(ConfigRepository.class);
    schedulerHandler = new SchedulerHandler(configRepository, schedulerJobClient);
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
    when(schedulerJobClient.createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE)).thenReturn(completedJob);

    schedulerHandler.checkSourceConnection(request);

    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(schedulerJobClient).createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE);
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
    when(schedulerJobClient.createGetSpecJob(SOURCE_DOCKER_IMAGE)).thenReturn(completedJob);

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
    verify(schedulerJobClient).createGetSpecJob(SOURCE_DOCKER_IMAGE);
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
    when(schedulerJobClient.createGetSpecJob(DESTINATION_DOCKER_IMAGE)).thenReturn(completedJob);

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
    verify(schedulerJobClient).createGetSpecJob(DESTINATION_DOCKER_IMAGE);
  }

  @Test
  public void testGetConnectorSpec() throws IOException, URISyntaxException {
    when(schedulerJobClient.createGetSpecJob(SOURCE_DOCKER_IMAGE)).thenReturn(completedJob);
    final StandardGetSpecOutput specOutput = new StandardGetSpecOutput().withSpecification(
        new ConnectorSpecification()
            .withDocumentationUrl(new URI("https://google.com"))
            .withChangelogUrl(new URI("https://google.com"))
            .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));
    final JobOutput jobOutput = mock(JobOutput.class);
    when(jobOutput.getGetSpec()).thenReturn(specOutput);
    when(completedJob.getSuccessOutput()).thenReturn(Optional.of(jobOutput));

    assertEquals(specOutput.getSpecification(), schedulerHandler.getConnectorSpecification(SOURCE_DOCKER_IMAGE));

    verify(schedulerJobClient).createGetSpecJob(SOURCE_DOCKER_IMAGE);
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
    when(schedulerJobClient.createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE)).thenReturn(completedJob);

    schedulerHandler.checkDestinationConnection(request);

    verify(configRepository).getDestinationConnection(destination.getDestinationId());
    verify(schedulerJobClient).createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE);
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
    when(schedulerJobClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE)).thenReturn(completedJob);
    final JobOutput jobOutput = new JobOutput()
        .withDiscoverCatalog(new StandardDiscoverCatalogOutput()
            .withCatalog(CatalogHelpers.createAirbyteCatalog("shoes", Field.of("sku", JsonSchemaPrimitive.STRING))));
    when(completedJob.getSuccessOutput()).thenReturn(Optional.of(jobOutput));

    schedulerHandler.discoverSchemaForSource(request);

    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(schedulerJobClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
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
    when(schedulerJobClient.createSyncJob(source, destination, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE)).thenReturn(completedJob);
    when(completedJob.getScope()).thenReturn("cat:12");
    final JobConfig jobConfig = mock(JobConfig.class);
    when(completedJob.getConfig()).thenReturn(jobConfig);
    when(jobConfig.getConfigType()).thenReturn(ConfigType.SYNC);

    final JobInfoRead jobStatusRead = schedulerHandler.syncConnection(request);

    assertEquals(io.airbyte.api.model.JobStatus.SUCCEEDED, jobStatusRead.getJob().getStatus());
    verify(configRepository).getStandardSync(standardSync.getConnectionId());
    verify(configRepository).getSourceConnection(standardSync.getSourceId());
    verify(configRepository).getDestinationConnection(standardSync.getDestinationId());
    verify(schedulerJobClient).createSyncJob(source, destination, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE);
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(StandardCheckConnectionOutput.Status.class, CheckConnectionRead.StatusEnum.class));
    assertTrue(Enums.isCompatible(JobStatus.class, io.airbyte.api.model.JobStatus.class));
  }

}
