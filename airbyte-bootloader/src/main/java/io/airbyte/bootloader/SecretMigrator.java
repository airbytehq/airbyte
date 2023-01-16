/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.Value;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class SecretMigrator {

  private final SecretsRepositoryReader secretsReader;
  private final SecretsRepositoryWriter secretsWriter;
  private final ConfigRepository configRepository;
  private final JobPersistence jobPersistence;
  private final Optional<SecretPersistence> secretPersistence;

  public SecretMigrator(final SecretsRepositoryReader secretsReader,
                        final SecretsRepositoryWriter secretsWriter,
                        final ConfigRepository configRepository,
                        final JobPersistence jobPersistence,
                        @Named("secretPersistence") final Optional<SecretPersistence> secretPersistence) {
    this.secretsReader = secretsReader;
    this.secretsWriter = secretsWriter;
    this.configRepository = configRepository;
    this.jobPersistence = jobPersistence;
    this.secretPersistence = secretPersistence;
  }

  @Value
  static class ConnectorConfiguration {

    private final UUID workspace;
    private final JsonNode configuration;
    private final JsonNode spec;

  }

  /**
   * Perform a secret migration. It will load all the actor specs extract the secret JsonPath from it.
   * Then for all the secret that are stored in a plain text format, it will save the plain text in
   * the secret manager and store the coordinate in the config DB.
   */
  public void migrateSecrets() throws Exception {
    if (secretPersistence.isEmpty()) {
      log.info("No secret persistence is provided, the migration won't be run ");

      return;
    } else {
      secretPersistence.get().initialize();
    }

    final List<StandardSourceDefinition> standardSourceDefinitions = configRepository.listStandardSourceDefinitions(true);

    final Map<UUID, ConnectorSpecification> definitionIdToSourceSpecs = standardSourceDefinitions
        .stream().collect(Collectors.toMap(StandardSourceDefinition::getSourceDefinitionId, StandardSourceDefinition::getSpec));

    final List<SourceConnection> sourcesWithoutSecrets = configRepository.listSourceConnection();
    final List<SourceConnection> sourcesWithSecrets = new ArrayList<>();
    for (final SourceConnection source : sourcesWithoutSecrets) {
      final SourceConnection sourceWithSecrets = secretsReader.getSourceConnectionWithSecrets(source.getSourceId());
      sourcesWithSecrets.add(sourceWithSecrets);
    }

    migrateSources(sourcesWithSecrets, definitionIdToSourceSpecs);

    final List<StandardDestinationDefinition> standardDestinationDefinitions = configRepository.listStandardDestinationDefinitions(true);

    final Map<UUID, ConnectorSpecification> definitionIdToDestinationSpecs = standardDestinationDefinitions.stream()
        .collect(Collectors.toMap(StandardDestinationDefinition::getDestinationDefinitionId, StandardDestinationDefinition::getSpec));

    final List<DestinationConnection> destinationsWithoutSecrets = configRepository.listDestinationConnection();
    final List<DestinationConnection> destinationsWithSecrets = new ArrayList<>();
    for (final DestinationConnection destination : destinationsWithoutSecrets) {
      final DestinationConnection destinationWithoutSecrets = secretsReader.getDestinationConnectionWithSecrets(destination.getDestinationId());
      destinationsWithSecrets.add(destinationWithoutSecrets);
    }

    migrateDestinations(destinationsWithSecrets, definitionIdToDestinationSpecs);

    jobPersistence.setSecretMigrationDone();
  }

  /**
   * This is migrating the secrets for the source actors
   */
  @VisibleForTesting
  void migrateSources(final List<SourceConnection> sources, final Map<UUID, ConnectorSpecification> definitionIdToSourceSpecs)
      throws JsonValidationException, IOException {
    log.info("Migrating Sources");
    for (final SourceConnection source : sources) {
      final Optional<ConnectorSpecification> specOptional = Optional.ofNullable(definitionIdToSourceSpecs.get(source.getSourceDefinitionId()));

      if (specOptional.isPresent()) {
        secretsWriter.writeSourceConnection(source, specOptional.get());
      } else {
        // if the spec can't be found, don't risk writing secrets to db. wipe out the configuration for the
        // connector.
        final SourceConnection sourceWithConfigRemoved = Jsons.clone(source);
        sourceWithConfigRemoved.setConfiguration(Jsons.emptyObject());
        secretsWriter.writeSourceConnection(sourceWithConfigRemoved, new ConnectorSpecification().withConnectionSpecification(Jsons.emptyObject()));
      }
    }
  }

  /**
   * This is migrating the secrets for the destination actors
   */
  @VisibleForTesting
  void migrateDestinations(final List<DestinationConnection> destinations, final Map<UUID, ConnectorSpecification> definitionIdToDestinationSpecs)
      throws JsonValidationException, IOException {
    log.info("Migration Destinations");
    for (final DestinationConnection destination : destinations) {
      final Optional<ConnectorSpecification> specOptional =
          Optional.ofNullable(definitionIdToDestinationSpecs.get(destination.getDestinationDefinitionId()));

      if (specOptional.isPresent()) {
        secretsWriter.writeDestinationConnection(destination, specOptional.get());
      } else {
        // if the spec can't be found, don't risk writing secrets to db. wipe out the configuration for the
        // connector.
        final DestinationConnection destinationWithConfigRemoved = Jsons.clone(destination);
        destinationWithConfigRemoved.setConfiguration(Jsons.emptyObject());
        secretsWriter.writeDestinationConnection(destinationWithConfigRemoved,
            new ConnectorSpecification().withConnectionSpecification(Jsons.emptyObject()));
      }
    }
  }

}
