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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.helpers.YamlListToStandardDefinitions;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.server.errors.KnownException;
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

public class DestinationDefinitionsHandler {

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

  private static DestinationDefinitionRead buildDestinationDefinitionRead(StandardDestinationDefinition standardDestinationDefinition) {
    try {
      return new DestinationDefinitionRead()
          .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
          .name(standardDestinationDefinition.getName())
          .dockerRepository(standardDestinationDefinition.getDockerRepository())
          .dockerImageTag(standardDestinationDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardDestinationDefinition.getDocumentationUrl()));
    } catch (URISyntaxException | NullPointerException e) {
      throw new KnownException(500, "Unable to process retrieved latest destination definitions list", e);
    }
  }

  public DestinationDefinitionReadList listDestinationDefinitions() throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationDefinitionRead> reads = configRepository
        .listStandardDestinationDefinitions()
        .stream()
        .map(DestinationDefinitionsHandler::buildDestinationDefinitionRead)
        .collect(Collectors.toList());

    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  public DestinationDefinitionReadList listLatestDestinationDefinitions() throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<StandardDestinationDefinition> destDefs;
    try {
      destDefs = YamlListToStandardDefinitions.toStandardDestinationDefinitions(getLatestDestinations());
    } catch (RuntimeException e) {
      throw new KnownException(500, "Error retrieving latest destination definitions", e);
    }
    final var reads = destDefs.stream().map(DestinationDefinitionsHandler::buildDestinationDefinitionRead).collect(Collectors.toList());
    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  private String getLatestDestinations() {
    try {
      return githubStore.getLatestDestinations();
    } catch (InterruptedException | IOException e) {
      throw new KnownException(500, "Request to retrieve latest destination definitions failed", e);
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
        .withName(destinationDefinitionCreate.getName());

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
        .withDocumentationUrl(currentDestination.getDocumentationUrl());

    configRepository.writeStandardDestinationDefinition(newDestination);
    // we want to re-fetch the spec for updated definitions.
    schedulerSynchronousClient.resetCache();
    return buildDestinationDefinitionRead(newDestination);
  }

}
