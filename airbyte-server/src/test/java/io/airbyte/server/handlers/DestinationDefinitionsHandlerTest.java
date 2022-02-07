/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.ReleaseStage;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousJobMetadata;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.time.LocalDate;
import java.util.Collections;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class DestinationDefinitionsHandlerTest {

  private static final String TODAY_DATE_STRING = LocalDate.now().toString();

  private ConfigRepository configRepository;
  private StandardDestinationDefinition destinationDefinition;
  private DestinationDefinitionsHandler destinationDefinitionsHandler;
  private Supplier<UUID> uuidSupplier;
  private SynchronousSchedulerClient schedulerSynchronousClient;
  private AirbyteGithubStore githubStore;
  private DestinationHandler destinationHandler;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    uuidSupplier = mock(Supplier.class);
    destinationDefinition = generateDestinationDefinition();
    schedulerSynchronousClient = spy(SynchronousSchedulerClient.class);
    githubStore = mock(AirbyteGithubStore.class);
    destinationHandler = mock(DestinationHandler.class);

    destinationDefinitionsHandler =
        new DestinationDefinitionsHandler(configRepository, uuidSupplier, schedulerSynchronousClient, githubStore, destinationHandler);
  }

  private StandardDestinationDefinition generateDestinationDefinition() {
    final ConnectorSpecification spec = new ConnectorSpecification().withConnectionSpecification(
        Jsons.jsonNode(ImmutableMap.of("foo", "bar")));

    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withName("presto")
        .withDockerImageTag("12.3")
        .withDockerRepository("repo")
        .withDocumentationUrl("https://hulu.com")
        .withIcon("http.svg")
        .withSpec(spec)
        .withTombstone(false)
        .withReleaseStage(StandardDestinationDefinition.ReleaseStage.ALPHA)
        .withReleaseDate(TODAY_DATE_STRING);
  }

  @Test
  @DisplayName("listDestinationDefinition should return the right list")
  void testListDestinations() throws JsonValidationException, IOException, URISyntaxException {
    final StandardDestinationDefinition destination2 = generateDestinationDefinition();

    when(configRepository.listStandardDestinationDefinitions(false)).thenReturn(Lists.newArrayList(destinationDefinition, destination2));

    final DestinationDefinitionRead expectedDestinationDefinitionRead1 = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()));

    final DestinationDefinitionRead expectedDestinationDefinitionRead2 = new DestinationDefinitionRead()
        .destinationDefinitionId(destination2.getDestinationDefinitionId())
        .name(destination2.getName())
        .dockerRepository(destination2.getDockerRepository())
        .dockerImageTag(destination2.getDockerImageTag())
        .documentationUrl(new URI(destination2.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destination2.getIcon()))
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()));

    final DestinationDefinitionReadList actualDestinationDefinitionReadList = destinationDefinitionsHandler.listDestinationDefinitions();

    assertEquals(
        Lists.newArrayList(expectedDestinationDefinitionRead1, expectedDestinationDefinitionRead2),
        actualDestinationDefinitionReadList.getDestinationDefinitions());
  }

  @Test
  @DisplayName("getDestinationDefinition should return the right destination")
  void testGetDestination() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);

    final DestinationDefinitionRead expectedDestinationDefinitionRead = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()));

    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody = new DestinationDefinitionIdRequestBody()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId());

    final DestinationDefinitionRead actualDestinationDefinitionRead =
        destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody);

    assertEquals(expectedDestinationDefinitionRead, actualDestinationDefinitionRead);
  }

  @Test
  @DisplayName("createDestinationDefinition should correctly create a destinationDefinition")
  void testCreateDestinationDefinition() throws URISyntaxException, IOException, JsonValidationException {
    final StandardDestinationDefinition destination = generateDestinationDefinition();
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());

    when(uuidSupplier.get()).thenReturn(destination.getDestinationDefinitionId());
    when(schedulerSynchronousClient.createGetSpecJob(imageName)).thenReturn(new SynchronousResponse<>(
        destination.getSpec(),
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final DestinationDefinitionCreate create = new DestinationDefinitionCreate()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .icon(destination.getIcon());

    final DestinationDefinitionRead expectedRead = new DestinationDefinitionRead()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .destinationDefinitionId(destination.getDestinationDefinitionId())
        .icon(DestinationDefinitionsHandler.loadIcon(destination.getIcon()))
        .releaseStage(ReleaseStage.CUSTOM);

    final DestinationDefinitionRead actualRead = destinationDefinitionsHandler.createCustomDestinationDefinition(create);

    assertEquals(expectedRead, actualRead);
    verify(schedulerSynchronousClient).createGetSpecJob(imageName);
    verify(configRepository).writeStandardDestinationDefinition(destination.withReleaseDate(null).withReleaseStage(
        StandardDestinationDefinition.ReleaseStage.CUSTOM));
  }

  @Test
  @DisplayName("updateDestinationDefinition should correctly update a destinationDefinition")
  void testUpdateDestination() throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId())).thenReturn(destinationDefinition);
    final DestinationDefinitionRead currentDestination = destinationDefinitionsHandler
        .getDestinationDefinition(
            new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationDefinition.getDestinationDefinitionId()));
    final String currentTag = currentDestination.getDockerImageTag();
    final String dockerRepository = currentDestination.getDockerRepository();
    final String newDockerImageTag = "averydifferenttag";
    assertNotEquals(newDockerImageTag, currentTag);

    final String newImageName = DockerUtils.getTaggedImageName(destinationDefinition.getDockerRepository(), newDockerImageTag);
    final ConnectorSpecification newSpec = new ConnectorSpecification().withConnectionSpecification(
        Jsons.jsonNode(ImmutableMap.of("foo2", "bar2")));
    when(schedulerSynchronousClient.createGetSpecJob(newImageName)).thenReturn(new SynchronousResponse<>(
        newSpec,
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final StandardDestinationDefinition updatedDestination =
        Jsons.clone(destinationDefinition).withDockerImageTag(newDockerImageTag).withSpec(newSpec);

    final DestinationDefinitionRead destinationRead = destinationDefinitionsHandler.updateDestinationDefinition(
        new DestinationDefinitionUpdate().destinationDefinitionId(this.destinationDefinition.getDestinationDefinitionId())
            .dockerImageTag(newDockerImageTag));

    assertEquals(newDockerImageTag, destinationRead.getDockerImageTag());
    verify(schedulerSynchronousClient).createGetSpecJob(newImageName);
    verify(configRepository).writeStandardDestinationDefinition(updatedDestination);
  }

  @Test
  @DisplayName("deleteDestinationDefinition should correctly delete a sourceDefinition")
  void testDeleteDestinationDefinition() throws ConfigNotFoundException, IOException, JsonValidationException {
    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody =
        new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationDefinition.getDestinationDefinitionId());
    final StandardDestinationDefinition updatedDestinationDefinition = Jsons.clone(this.destinationDefinition).withTombstone(true);
    final DestinationRead destination = new DestinationRead();

    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);
    when(destinationHandler.listDestinationsForDestinationDefinition(destinationDefinitionIdRequestBody))
        .thenReturn(new DestinationReadList().destinations(Collections.singletonList(destination)));

    assertFalse(destinationDefinition.getTombstone());

    destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);

    verify(destinationHandler).deleteDestination(destination);
    verify(configRepository).writeStandardDestinationDefinition(updatedDestinationDefinition);
  }

  @Nested
  @DisplayName("listLatest")
  class listLatest {

    @Test
    @DisplayName("should return the latest list")
    void testCorrect() throws InterruptedException {
      final StandardDestinationDefinition destinationDefinition = generateDestinationDefinition();
      when(githubStore.getLatestDestinations()).thenReturn(Collections.singletonList(destinationDefinition));

      final var destinationDefinitionReadList = destinationDefinitionsHandler.listLatestDestinationDefinitions().getDestinationDefinitions();
      assertEquals(1, destinationDefinitionReadList.size());

      final var destinationDefinitionRead = destinationDefinitionReadList.get(0);
      assertEquals(DestinationDefinitionsHandler.buildDestinationDefinitionRead(destinationDefinition), destinationDefinitionRead);
    }

    @Test
    @DisplayName("returns empty collection if cannot find latest definitions")
    void testHttpTimeout() {
      assertEquals(0, destinationDefinitionsHandler.listLatestDestinationDefinitions().getDestinationDefinitions().size());
    }

  }

}
