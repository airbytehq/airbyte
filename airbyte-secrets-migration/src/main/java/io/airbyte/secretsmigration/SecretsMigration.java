/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.secretsmigration;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.Configs;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.LocalTestingSecretPersistence;
import io.airbyte.config.persistence.split_secrets.RealSecretsHydrator;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.BucketSpecCacheSchedulerClient;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.SourceHandler;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SecretsMigration {

  public static void main(final String[] args) throws Exception {
    final Configs configs = new EnvConfigs();

    final Database database = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
        .getInitialized();

    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(database).withValidation();

    final ConfigRepository configRepository =
        new ConfigRepository(
            configPersistence,
            SecretPersistence.getSecretsHydrator(configs),
            SecretPersistence.getLongLived(configs),
            SecretPersistence.getEphemeral(configs));

    final SpecFetcher specFetcher = new SimpleSpecFetcher();

    configRepository.setSpecFetcher(image -> Exceptions.toRuntime(() -> specFetcher.execute(image)));

    for (final SourceConnection source : configRepository.listSourceConnectionWithSecrets()) {
      System.out.println("source: " + source.getSourceId());
      final var definition = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
      final var connectorSpec = SourceHandler.getSpecFromSourceDefinitionId(specFetcher, definition);
      configRepository.writeSourceConnection(source, connectorSpec);
    }

    for (final DestinationConnection destination : configRepository.listDestinationConnectionWithSecrets()) {
      System.out.println("destination: " + destination.getDestinationId());
      final var definition = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
      final var connectorSpec = DestinationHandler.getSpec(specFetcher, definition);
      configRepository.writeDestinationConnection(destination, connectorSpec);
    }
  }

  private static class SimpleSpecFetcher extends SpecFetcher {

    public SimpleSpecFetcher() {
      super(null);
    }

    @Override
    public ConnectorSpecification execute(final String dockerImage) throws IOException {
      return BucketSpecCacheSchedulerClient
          .attemptToFetchSpecFromBucket(StorageOptions.getDefaultInstance().getService(), "io-airbyte-cloud-spec-cache", dockerImage).get();
    }
  }

}
