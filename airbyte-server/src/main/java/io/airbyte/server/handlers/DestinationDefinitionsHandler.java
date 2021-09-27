/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.server.errors.InternalServerKnownException;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DestinationDefinitionsHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(DestinationDefinitionsHandler.class);

  private final DockerImageValidator imageValidator;
  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final CachingSynchronousSchedulerClient schedulerSynchronousClient;
  private final AirbyteGithubStore githubStore;

  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final DockerImageValidator imageValidator,
                                       final CachingSynchronousSchedulerClient schedulerSynchronousClient) {
    this(configRepository, imageValidator, UUID::randomUUID, schedulerSynchronousClient, AirbyteGithubStore.production());
  }

  @VisibleForTesting
  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final DockerImageValidator imageValidator,
                                       final Supplier<UUID> uuidSupplier,
                                       final CachingSynchronousSchedulerClient schedulerSynchronousClient,
                                       final AirbyteGithubStore githubStore) {
    this.configRepository = configRepository;
    this.imageValidator = imageValidator;
    this.uuidSupplier = uuidSupplier;
    this.schedulerSynchronousClient = schedulerSynchronousClient;
    this.githubStore = githubStore;
  }

  @VisibleForTesting
  static DestinationDefinitionRead buildDestinationDefinitionRead(StandardDestinationDefinition standardDestinationDefinition) {
    try {
      return new DestinationDefinitionRead()
          .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
          .name(standardDestinationDefinition.getName())
          .dockerRepository(standardDestinationDefinition.getDockerRepository())
          .dockerImageTag(standardDestinationDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardDestinationDefinition.getDocumentationUrl()))
          .icon(loadIcon(standardDestinationDefinition.getIcon()));
    } catch (URISyntaxException | NullPointerException e) {
      throw new InternalServerKnownException("Unable to process retrieved latest destination definitions list", e);
    }
  }

  public DestinationDefinitionReadList listDestinationDefinitions() throws IOException, JsonValidationException {
    return toDestinationDefinitionReadList(configRepository.listStandardDestinationDefinitions());
  }

  private static DestinationDefinitionReadList toDestinationDefinitionReadList(List<StandardDestinationDefinition> defs) {
    final List<DestinationDefinitionRead> reads = defs.stream()
        .map(DestinationDefinitionsHandler::buildDestinationDefinitionRead)
        .collect(Collectors.toList());
    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return toDestinationDefinitionReadList(getLatestDestinations());
  }

  private List<StandardDestinationDefinition> getLatestDestinations() {
    try {
      return githubStore.getLatestDestinations();
    } catch (InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest destination definitions failed", e);
    }
  }

  public DestinationDefinitionRead getDestinationDefinition(DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildDestinationDefinitionRead(
        configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId()));
  }

  public DestinationDefinitionRead createDestinationDefinition(DestinationDefinitionCreate destinationDefinitionCreate)
      throws JsonValidationException, IOException {
    imageValidator.assertValidIntegrationImage(destinationDefinitionCreate.getDockerRepository(),
        destinationDefinitionCreate.getDockerImageTag());

    final UUID id = uuidSupplier.get();
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(id)
        .withDockerRepository(destinationDefinitionCreate.getDockerRepository())
        .withDockerImageTag(destinationDefinitionCreate.getDockerImageTag())
        .withDocumentationUrl(destinationDefinitionCreate.getDocumentationUrl().toString())
        .withName(destinationDefinitionCreate.getName())
        .withIcon(destinationDefinitionCreate.getIcon());

    configRepository.writeStandardDestinationDefinition(destinationDefinition);

    return buildDestinationDefinitionRead(destinationDefinition);
  }

  public DestinationDefinitionRead updateDestinationDefinition(DestinationDefinitionUpdate destinationDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardDestinationDefinition currentDestination = configRepository
        .getStandardDestinationDefinition(destinationDefinitionUpdate.getDestinationDefinitionId());
    imageValidator.assertValidIntegrationImage(currentDestination.getDockerRepository(),
        destinationDefinitionUpdate.getDockerImageTag());

    final StandardDestinationDefinition newDestination = new StandardDestinationDefinition()
        .withDestinationDefinitionId(currentDestination.getDestinationDefinitionId())
        .withDockerImageTag(destinationDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentDestination.getDockerRepository())
        .withName(currentDestination.getName())
        .withDocumentationUrl(currentDestination.getDocumentationUrl())
        .withIcon(currentDestination.getIcon());

    configRepository.writeStandardDestinationDefinition(newDestination);
    // we want to re-fetch the spec for updated definitions.
    schedulerSynchronousClient.resetCache();
    return buildDestinationDefinitionRead(newDestination);
  }

  public static String loadIcon(String name) {
    try {
      return name == null ? null : MoreResources.readResource("icons/" + name);
    } catch (Exception e) {
      return null;
    }
  }

}
