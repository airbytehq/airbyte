/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;

public class ConfigurationUpdate {

  private final ConfigRepository configRepository;
  private final SpecFetcher specFetcher;
  private final JsonSecretsProcessor secretsProcessor;

  public ConfigurationUpdate(ConfigRepository configRepository, SpecFetcher specFetcher) {
    this(configRepository, specFetcher, new JsonSecretsProcessor());
  }

  public ConfigurationUpdate(ConfigRepository configRepository, SpecFetcher specFetcher, JsonSecretsProcessor secretsProcessor) {
    this.configRepository = configRepository;
    this.specFetcher = specFetcher;
    this.secretsProcessor = secretsProcessor;
  }

  public SourceConnection source(UUID sourceId, String sourceName, JsonNode newConfiguration)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing source
    final SourceConnection persistedSource = configRepository.getSourceConnectionWithSecrets(sourceId);
    persistedSource.setName(sourceName);
    // get spec
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(persistedSource.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDefinition.getDockerRepository(), sourceDefinition.getDockerImageTag());
    final ConnectorSpecification spec = specFetcher.execute(imageName);
    // copy any necessary secrets from the current source to the incoming updated source
    final JsonNode updatedConfiguration = secretsProcessor.copySecrets(
        persistedSource.getConfiguration(),
        newConfiguration,
        spec.getConnectionSpecification());

    return Jsons.clone(persistedSource).withConfiguration(updatedConfiguration);
  }

  public DestinationConnection destination(UUID destinationId, String destName, JsonNode newConfiguration)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing destination
    final DestinationConnection persistedDestination = configRepository.getDestinationConnectionWithSecrets(destinationId);
    persistedDestination.setName(destName);
    // get spec
    final StandardDestinationDefinition destinationDefinition = configRepository
        .getStandardDestinationDefinition(persistedDestination.getDestinationDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(destinationDefinition.getDockerRepository(), destinationDefinition.getDockerImageTag());
    final ConnectorSpecification spec = specFetcher.execute(imageName);
    // copy any necessary secrets from the current destination to the incoming updated destination
    final JsonNode updatedConfiguration = secretsProcessor.copySecrets(
        persistedDestination.getConfiguration(),
        newConfiguration,
        spec.getConnectionSpecification());

    return Jsons.clone(persistedDestination).withConfiguration(updatedConfiguration);
  }

}
