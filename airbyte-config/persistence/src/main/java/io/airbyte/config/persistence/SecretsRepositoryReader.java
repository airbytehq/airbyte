/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StagingConfiguration;
import io.airbyte.config.persistence.split_secrets.SecretsHelpers;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is responsible for fetching both connectors and their secrets (from separate secrets
 * stores). All methods in this class return secrets! Use it carefully.
 */
public class SecretsRepositoryReader {

  private static final Logger LOGGER = LoggerFactory.getLogger(SecretsRepositoryReader.class);

  private final ConfigRepository configRepository;
  private final SecretsHydrator secretsHydrator;

  public SecretsRepositoryReader(final ConfigRepository configRepository,
                                 final SecretsHydrator secretsHydrator) {
    this.configRepository = configRepository;
    this.secretsHydrator = secretsHydrator;
  }

  public SourceConnection getSourceConnectionWithSecrets(final UUID sourceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final var source = configRepository.getSourceConnection(sourceId);
    return hydrateSourcePartialConfig(source);
  }

  public List<SourceConnection> listSourceConnectionWithSecrets() throws JsonValidationException, IOException {
    final var sources = configRepository.listSourceConnection();

    return sources
        .stream()
        .map(partialSource -> Exceptions.toRuntime(() -> hydrateSourcePartialConfig(partialSource)))
        .collect(Collectors.toList());
  }

  public DestinationConnection getDestinationConnectionWithSecrets(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final var destination = configRepository.getDestinationConnection(destinationId);
    return hydrateDestinationPartialConfig(destination);
  }

  public List<DestinationConnection> listDestinationConnectionWithSecrets() throws JsonValidationException, IOException {
    final var destinations = configRepository.listDestinationConnection();

    return destinations
        .stream()
        .map(partialDestination -> Exceptions.toRuntime(() -> hydrateDestinationPartialConfig(partialDestination)))
        .collect(Collectors.toList());
  }

  public Map<String, Stream<JsonNode>> dumpConfigsWithSecrets() throws IOException {
    final Map<String, Stream<JsonNode>> dump = new HashMap<>(configRepository.dumpConfigsNoSecrets());
    final String sourceKey = ConfigSchema.SOURCE_CONNECTION.name();
    final String destinationKey = ConfigSchema.DESTINATION_CONNECTION.name();

    hydrateValuesIfKeyPresent(sourceKey, dump);
    hydrateValuesIfKeyPresent(destinationKey, dump);
    hydrateStagingConfig(dump);

    return dump;
  }

  private SourceConnection hydrateSourcePartialConfig(final SourceConnection sourceWithPartialConfig) {
    final JsonNode hydratedConfig = secretsHydrator.hydrate(sourceWithPartialConfig.getConfiguration());
    return Jsons.clone(sourceWithPartialConfig).withConfiguration(hydratedConfig);
  }

  private DestinationConnection hydrateDestinationPartialConfig(final DestinationConnection sourceWithPartialConfig) {
    final JsonNode hydratedConfig = secretsHydrator.hydrate(sourceWithPartialConfig.getConfiguration());
    return Jsons.clone(sourceWithPartialConfig).withConfiguration(hydratedConfig);
  }

  private void hydrateValuesIfKeyPresent(final String key, final Map<String, Stream<JsonNode>> dump) {
    if (dump.containsKey(key)) {
      final Stream<JsonNode> augmentedValue = dump.get(key).map(secretsHydrator::hydrate);
      dump.put(key, augmentedValue);
    }
  }

  private void hydrateStagingConfig(final Map<String, Stream<JsonNode>> dump) {
    if (dump.containsKey(ConfigSchema.STAGING_CONFIGURATION.name())) {
      Stream<JsonNode> augmentedValue = dump.get(ConfigSchema.STAGING_CONFIGURATION.name()).map(c -> Jsons.object(c, StagingConfiguration.class))
          .map(c -> {
            try {
              return Jsons.jsonNode(getStagingConfigurationWithSecrets(c.getDestinationDefinitionId()));
            } catch (final JsonValidationException | ConfigNotFoundException | IOException e) {
              throw new RuntimeException(e);
            }
          });
      dump.put(ConfigSchema.STAGING_CONFIGURATION.name(), augmentedValue);
    }
  }

  public StagingConfiguration getStagingConfigurationWithSecrets(final UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StagingConfiguration stagingConfiguration = configRepository.getStagingConfigurationNoSecrets(destinationDefinitionId);

    final JsonNode secret = SecretsHelpers.decryptStagingConfiguration(stagingConfiguration, secretsHydrator);
    return Jsons.clone(stagingConfiguration).withConfiguration(secret);
  }

}
