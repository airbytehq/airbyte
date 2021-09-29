/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.SourceDefinitionCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionRead;
import io.airbyte.api.model.SourceDefinitionReadList;
import io.airbyte.api.model.SourceDefinitionUpdate;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.StandardSourceDefinition;
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

public class SourceDefinitionsHandler {

  private final DockerImageValidator imageValidator;
  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final AirbyteGithubStore githubStore;
  private final CachingSynchronousSchedulerClient schedulerSynchronousClient;

  public SourceDefinitionsHandler(
                                  final ConfigRepository configRepository,
                                  final DockerImageValidator imageValidator,
                                  final CachingSynchronousSchedulerClient schedulerSynchronousClient) {
    this(configRepository, imageValidator, UUID::randomUUID, schedulerSynchronousClient, AirbyteGithubStore.production());
  }

  public SourceDefinitionsHandler(
                                  final ConfigRepository configRepository,
                                  final DockerImageValidator imageValidator,
                                  final Supplier<UUID> uuidSupplier,
                                  final CachingSynchronousSchedulerClient schedulerSynchronousClient,
                                  final AirbyteGithubStore githubStore) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.imageValidator = imageValidator;
    this.schedulerSynchronousClient = schedulerSynchronousClient;
    this.githubStore = githubStore;
  }

  @VisibleForTesting
  static SourceDefinitionRead buildSourceDefinitionRead(StandardSourceDefinition standardSourceDefinition) {
    try {
      return new SourceDefinitionRead()
          .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
          .name(standardSourceDefinition.getName())
          .dockerRepository(standardSourceDefinition.getDockerRepository())
          .dockerImageTag(standardSourceDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardSourceDefinition.getDocumentationUrl()))
          .icon(loadIcon(standardSourceDefinition.getIcon()));
    } catch (URISyntaxException | NullPointerException e) {
      throw new InternalServerKnownException("Unable to process retrieved latest source definitions list", e);
    }
  }

  public SourceDefinitionReadList listSourceDefinitions() throws IOException, JsonValidationException {
    return toSourceDefinitionReadList(configRepository.listStandardSources());
  }

  private static SourceDefinitionReadList toSourceDefinitionReadList(List<StandardSourceDefinition> defs) {
    final List<SourceDefinitionRead> reads = defs.stream()
        .map(SourceDefinitionsHandler::buildSourceDefinitionRead)
        .collect(Collectors.toList());
    return new SourceDefinitionReadList().sourceDefinitions(reads);
  }

  public SourceDefinitionReadList listLatestSourceDefinitions() {
    return toSourceDefinitionReadList(getLatestSources());
  }

  private List<StandardSourceDefinition> getLatestSources() {
    try {
      return githubStore.getLatestSources();
    } catch (InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest destination definitions failed", e);
    }
  }

  public SourceDefinitionRead getSourceDefinition(SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildSourceDefinitionRead(configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId()));
  }

  public SourceDefinitionRead createSourceDefinition(SourceDefinitionCreate sourceDefinitionCreate) throws JsonValidationException, IOException {
    imageValidator.assertValidIntegrationImage(sourceDefinitionCreate.getDockerRepository(), sourceDefinitionCreate.getDockerImageTag());

    final UUID id = uuidSupplier.get();
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(id)
        .withDockerRepository(sourceDefinitionCreate.getDockerRepository())
        .withDockerImageTag(sourceDefinitionCreate.getDockerImageTag())
        .withDocumentationUrl(sourceDefinitionCreate.getDocumentationUrl().toString())
        .withName(sourceDefinitionCreate.getName())
        .withIcon(sourceDefinitionCreate.getIcon());

    configRepository.writeStandardSource(sourceDefinition);

    return buildSourceDefinitionRead(sourceDefinition);
  }

  public SourceDefinitionRead updateSourceDefinition(SourceDefinitionUpdate sourceDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition currentSourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionUpdate.getSourceDefinitionId());
    imageValidator.assertValidIntegrationImage(currentSourceDefinition.getDockerRepository(), sourceDefinitionUpdate.getDockerImageTag());

    final StandardSourceDefinition newSource = new StandardSourceDefinition()
        .withSourceDefinitionId(currentSourceDefinition.getSourceDefinitionId())
        .withDockerImageTag(sourceDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentSourceDefinition.getDockerRepository())
        .withDocumentationUrl(currentSourceDefinition.getDocumentationUrl())
        .withName(currentSourceDefinition.getName())
        .withIcon(currentSourceDefinition.getIcon());

    configRepository.writeStandardSource(newSource);
    // we want to re-fetch the spec for updated definitions.
    schedulerSynchronousClient.resetCache();
    return buildSourceDefinitionRead(newSource);
  }

  public static String loadIcon(String name) {
    try {
      return name == null ? null : MoreResources.readResource("icons/" + name);
    } catch (Exception e) {
      return null;
    }
  }

}
