/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class DestinationDefinitionsHandlerTest {

  private DockerImageValidator dockerImageValidator;
  private ConfigRepository configRepository;
  private StandardDestinationDefinition destination;
  private DestinationDefinitionsHandler destinationHandler;
  private Supplier<UUID> uuidSupplier;
  private CachingSynchronousSchedulerClient schedulerSynchronousClient;
  private AirbyteGithubStore githubStore;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    uuidSupplier = mock(Supplier.class);
    dockerImageValidator = mock(DockerImageValidator.class);
    destination = generateDestination();
    schedulerSynchronousClient = spy(CachingSynchronousSchedulerClient.class);
    githubStore = mock(AirbyteGithubStore.class);

    destinationHandler =
        new DestinationDefinitionsHandler(configRepository, dockerImageValidator, uuidSupplier, schedulerSynchronousClient, githubStore);
  }

  private StandardDestinationDefinition generateDestination() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withName("presto")
        .withDockerImageTag("12.3")
        .withDockerRepository("repo")
        .withDocumentationUrl("https://hulu.com")
        .withIcon("http.svg");
  }

  @Test
  @DisplayName("listDestinationDefinition should return the right list")
  void testListDestinations() throws JsonValidationException, IOException, URISyntaxException {
    final StandardDestinationDefinition destination2 = generateDestination();

    when(configRepository.listStandardDestinationDefinitions()).thenReturn(Lists.newArrayList(destination, destination2));

    final DestinationDefinitionRead expectedDestinationDefinitionRead1 = new DestinationDefinitionRead()
        .destinationDefinitionId(destination.getDestinationDefinitionId())
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destination.getIcon()));

    final DestinationDefinitionRead expectedDestinationDefinitionRead2 = new DestinationDefinitionRead()
        .destinationDefinitionId(destination2.getDestinationDefinitionId())
        .name(destination2.getName())
        .dockerRepository(destination2.getDockerRepository())
        .dockerImageTag(destination2.getDockerImageTag())
        .documentationUrl(new URI(destination2.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destination2.getIcon()));

    final DestinationDefinitionReadList actualDestinationDefinitionReadList = destinationHandler.listDestinationDefinitions();

    assertEquals(
        Lists.newArrayList(expectedDestinationDefinitionRead1, expectedDestinationDefinitionRead2),
        actualDestinationDefinitionReadList.getDestinationDefinitions());
  }

  @Test
  @DisplayName("getDestinationDefinition should return the right destination")
  void testGetDestination() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(destination);

    final DestinationDefinitionRead expectedDestinationDefinitionRead = new DestinationDefinitionRead()
        .destinationDefinitionId(destination.getDestinationDefinitionId())
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destination.getIcon()));

    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody = new DestinationDefinitionIdRequestBody()
        .destinationDefinitionId(destination.getDestinationDefinitionId());

    final DestinationDefinitionRead actualDestinationDefinitionRead = destinationHandler.getDestinationDefinition(destinationDefinitionIdRequestBody);

    assertEquals(expectedDestinationDefinitionRead, actualDestinationDefinitionRead);
  }

  @Test
  @DisplayName("createDestinationDefinition should correctly create a destinationDefinition")
  void testCreateDestinationDefinition() throws URISyntaxException, IOException, JsonValidationException {
    final StandardDestinationDefinition destination = generateDestination();
    when(uuidSupplier.get()).thenReturn(destination.getDestinationDefinitionId());
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
        .icon(DestinationDefinitionsHandler.loadIcon(destination.getIcon()));

    final DestinationDefinitionRead actualRead = destinationHandler.createDestinationDefinition(create);

    assertEquals(expectedRead, actualRead);
    verify(dockerImageValidator).assertValidIntegrationImage(destination.getDockerRepository(), destination.getDockerImageTag());
  }

  @Test
  @DisplayName("updateDestinationDefinition should correctly update a destinationDefinition")
  void testUpdateDestination() throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId())).thenReturn(destination);
    final DestinationDefinitionRead currentDestination = destinationHandler
        .getDestinationDefinition(new DestinationDefinitionIdRequestBody().destinationDefinitionId(destination.getDestinationDefinitionId()));
    final String currentTag = currentDestination.getDockerImageTag();
    final String dockerRepository = currentDestination.getDockerRepository();
    final String newDockerImageTag = "averydifferenttag";
    assertNotEquals(newDockerImageTag, currentTag);

    final DestinationDefinitionRead sourceRead = destinationHandler.updateDestinationDefinition(
        new DestinationDefinitionUpdate().destinationDefinitionId(this.destination.getDestinationDefinitionId()).dockerImageTag(newDockerImageTag));

    assertEquals(newDockerImageTag, sourceRead.getDockerImageTag());
    verify(dockerImageValidator).assertValidIntegrationImage(dockerRepository, newDockerImageTag);
    verify(schedulerSynchronousClient).resetCache();
  }

  @Nested
  @DisplayName("listLatest")
  class listLatest {

    @Test
    @DisplayName("should return the latest list")
    void testCorrect() throws InterruptedException {
      final StandardDestinationDefinition destinationDefinition = generateDestination();
      when(githubStore.getLatestDestinations()).thenReturn(Collections.singletonList(destinationDefinition));

      final var destinationDefinitionReadList = destinationHandler.listLatestDestinationDefinitions().getDestinationDefinitions();
      assertEquals(1, destinationDefinitionReadList.size());

      final var destinationDefinitionRead = destinationDefinitionReadList.get(0);
      assertEquals(DestinationDefinitionsHandler.buildDestinationDefinitionRead(destinationDefinition), destinationDefinitionRead);
    }

    @Test
    @DisplayName("returns empty collection if cannot find latest definitions")
    void testHttpTimeout() {
      assertEquals(0, destinationHandler.listLatestDestinationDefinitions().getDestinationDefinitions().size());
    }

  }

}
