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
import io.airbyte.config.persistence.ConfigNotFoundException;
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
import io.airbyte.validation.json.JsonValidationException;
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

    System.out.println("listing sources...");
    for (final SourceConnection sourceWithoutSecrets : configRepository.listSourceConnection()) {
      System.out.println("getting source...");
      final var source = configRepository.getSourceConnectionWithSecrets(sourceWithoutSecrets.getSourceId());
      try {
        System.out.println("getting definition...");
        final var definition = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
        System.out.println("getting connector spec...");
        final var connectorSpec = SourceHandler.getSpecFromSourceDefinitionId(specFetcher, definition);
        System.out.println("writing source...");
        configRepository.writeSourceConnection(source, connectorSpec);
        System.out.println("source_pass: " + source.getSourceId());
      } catch (Throwable e) {
        System.out.println("source_" + e.getClass()  + ": " + source.getSourceId());
        e.printStackTrace();
      }
    }

    for (final DestinationConnection destinationWithoutSecrets : configRepository.listDestinationConnection()) {
      final var destination = configRepository.getDestinationConnectionWithSecrets(destinationWithoutSecrets.getDestinationId());
      try {
        final var definition = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
        final var connectorSpec = DestinationHandler.getSpec(specFetcher, definition);
        configRepository.writeDestinationConnection(destination, connectorSpec);
        System.out.println("destination_pass: " + destination.getDestinationId());
      } catch (Throwable e) {
        System.out.println("destination_" + e.getClass()  + ": " + destination.getDestinationId());
        e.printStackTrace();
      }
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
