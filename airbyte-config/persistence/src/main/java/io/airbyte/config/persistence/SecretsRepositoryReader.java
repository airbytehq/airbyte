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

  // private final ConfigPersistence persistence;
  private final ConfigRepository configRepository;
  private final SecretsHydrator secretsHydrator;

  public SecretsRepositoryReader(final ConfigRepository configRepository,
                                 final SecretsHydrator secretsHydrator) {
    this.configRepository = configRepository;
    this.secretsHydrator = secretsHydrator;
  }

  public SourceConnection getSourceConnectionWithSecrets(final UUID sourceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final var source = configRepository.getSourceConnection(sourceId);
    final var fullConfig = secretsHydrator.hydrate(source.getConfiguration());
    return Jsons.clone(source).withConfiguration(fullConfig);
  }

  public List<SourceConnection> listSourceConnectionWithSecrets() throws JsonValidationException, IOException {
    final var sources = configRepository.listSourceConnection();

    return sources
        .stream()
        .map(partialSource -> Exceptions.toRuntime(() -> getSourceConnectionWithSecrets(partialSource.getSourceId())))
        .collect(Collectors.toList());
  }

  public DestinationConnection getDestinationConnectionWithSecrets(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final var destination = configRepository.getDestinationConnection(destinationId);
    final var fullConfig = secretsHydrator.hydrate(destination.getConfiguration());
    return Jsons.clone(destination).withConfiguration(fullConfig);
  }

  public List<DestinationConnection> listDestinationConnectionWithSecrets() throws JsonValidationException, IOException {
    final var destinations = configRepository.listDestinationConnection();

    return destinations
        .stream()
        .map(partialDestination -> Exceptions.toRuntime(() -> getDestinationConnectionWithSecrets(partialDestination.getDestinationId())))
        .collect(Collectors.toList());
  }

  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    final var map = new HashMap<>(configRepository.dumpConfigsNoSecrets());
    final var sourceKey = ConfigSchema.SOURCE_CONNECTION.name();
    final var destinationKey = ConfigSchema.DESTINATION_CONNECTION.name();

    if (map.containsKey(sourceKey)) {
      final Stream<JsonNode> augmentedValue = map.get(sourceKey).map(secretsHydrator::hydrate);
      map.put(sourceKey, augmentedValue);
    }

    if (map.containsKey(destinationKey)) {
      final Stream<JsonNode> augmentedValue = map.get(destinationKey).map(secretsHydrator::hydrate);
      map.put(destinationKey, augmentedValue);
    }

    return map;
  }

}
