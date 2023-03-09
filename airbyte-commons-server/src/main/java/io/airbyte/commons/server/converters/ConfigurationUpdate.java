/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.UUID;

@Singleton
public class ConfigurationUpdate {

  private final ConfigRepository configRepository;
  private final SecretsRepositoryReader secretsRepositoryReader;
  private final JsonSecretsProcessor secretsProcessor;

  public ConfigurationUpdate(final ConfigRepository configRepository, final SecretsRepositoryReader secretsRepositoryReader) {
    this(configRepository, secretsRepositoryReader, JsonSecretsProcessor.builder()
        .copySecrets(true)
        .build());
  }

  public ConfigurationUpdate(final ConfigRepository configRepository,
                             final SecretsRepositoryReader secretsRepositoryReader,
                             final JsonSecretsProcessor secretsProcessor) {
    this.configRepository = configRepository;
    this.secretsRepositoryReader = secretsRepositoryReader;
    this.secretsProcessor = secretsProcessor;
  }

  public SourceConnection source(final UUID sourceId, final String sourceName, final JsonNode newConfiguration)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing source
    final SourceConnection persistedSource = secretsRepositoryReader.getSourceConnectionWithSecrets(sourceId);
    persistedSource.setName(sourceName);
    // get spec
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(persistedSource.getSourceDefinitionId());
    final ConnectorSpecification spec = sourceDefinition.getSpec();
    // copy any necessary secrets from the current source to the incoming updated source
    final JsonNode updatedConfiguration = secretsProcessor.copySecrets(
        persistedSource.getConfiguration(),
        newConfiguration,
        spec.getConnectionSpecification());

    return Jsons.clone(persistedSource).withConfiguration(updatedConfiguration);
  }

  public DestinationConnection destination(final UUID destinationId, final String destName, final JsonNode newConfiguration)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing destination
    final DestinationConnection persistedDestination = secretsRepositoryReader.getDestinationConnectionWithSecrets(destinationId);
    persistedDestination.setName(destName);
    // get spec
    final StandardDestinationDefinition destinationDefinition = configRepository
        .getStandardDestinationDefinition(persistedDestination.getDestinationDefinitionId());
    final ConnectorSpecification spec = destinationDefinition.getSpec();
    // copy any necessary secrets from the current destination to the incoming updated destination
    final JsonNode updatedConfiguration = secretsProcessor.copySecrets(
        persistedDestination.getConfiguration(),
        newConfiguration,
        spec.getConnectionSpecification());

    return Jsons.clone(persistedDestination).withConfiguration(updatedConfiguration);
  }

}
