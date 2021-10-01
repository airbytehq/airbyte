/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.secretsmigration;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.scheduler.client.BucketSpecCacheSchedulerClient;
import io.airbyte.scheduler.client.SpecCachingSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.converters.SpecFetcher;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SecretsMigration {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final Logger LOGGER = LoggerFactory.getLogger(SecretsMigration.class);
  final Configs configs;
  final boolean dryRun;
  final ConfigRepository readFrom;
  final ConfigRepository writeTo;

  public SecretsMigration(Configs envConfigs, ConfigRepository readFrom, ConfigRepository writeTo, boolean dryRun) {
    this.configs = envConfigs;
    this.readFrom = readFrom;
    this.writeTo = writeTo;
    this.dryRun = dryRun;
  }

  public void run() throws IOException {
    LOGGER.info("Starting migration run.");

    LOGGER.info("... Dry Run: deserializing configurations and writing to the new store...");
    Map<String, Stream<JsonNode>> configurations = readFrom.dumpConfigs();

    final var sourceCount = new AtomicInteger(0);
    final var destinationCount = new AtomicInteger(0);
    final var otherCount = new AtomicInteger(0);

    for (String configSchemaName : configurations.keySet()) {
      configurations.put(configSchemaName,
          configurations.get(configSchemaName).peek(configJson -> {
            Class<Object> className = ConfigSchema.valueOf(configSchemaName).getClassName();
            Object object = Jsons.object(configJson, className);

            if (className.getSimpleName().equals("SourceConnection")) {
              LOGGER.info("SOURCE_CONNECTION " + ((SourceConnection) object).getSourceId());
              sourceCount.incrementAndGet();
            } else if (className.getSimpleName().equals("DestinationConnection")) {
              LOGGER.info("DESTINATION_CONNECTION " + ((DestinationConnection) object).getDestinationId());
              destinationCount.incrementAndGet();
            } else {
              LOGGER.info("className.getSimpleName(): " + className.getSimpleName());
              otherCount.incrementAndGet();
            }
          }));
    }

    writeTo.replaceAllConfigsDeserializing(configurations, true);

    LOGGER.info("sourceCount = " + sourceCount.get());
    LOGGER.info("destinationCount = " + destinationCount.get());
    LOGGER.info("otherCount = " + otherCount.get());

     LOGGER.info("... With dryRun=" + dryRun + ": deserializing configurations and writing to the new store...");
     configurations = readFrom.dumpConfigs();
     writeTo.replaceAllConfigsDeserializing(configurations, dryRun);

    LOGGER.info("Migration run complete.");
  }

  public static void main(String[] args) throws Exception {
    final Configs configs = new EnvConfigs();
    final ConfigPersistence dbPersistence = new DatabaseConfigPersistence(new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized()).withValidation();

    final ConfigRepository readFromConfigRepository =
        new ConfigRepository(dbPersistence, new NoOpSecretsHydrator(), Optional.empty(), Optional.empty());

    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configs);
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configs);

    LOGGER.info("secretPersistence.isPresent() = " + secretPersistence.isPresent());
    LOGGER.info("ephemeralSecretPersistence.isPresent() = " + ephemeralSecretPersistence.isPresent());

    final ConfigRepository writeToConfigRepository =
        new ConfigRepository(dbPersistence, secretsHydrator, secretPersistence, ephemeralSecretPersistence);

    final SynchronousSchedulerClient bucketSpecCacheSchedulerClient =
        new BucketSpecCacheSchedulerClient(new FakeSyncSchedulerClient(), configs.getSpecCacheBucket());
    final SpecCachingSynchronousSchedulerClient cachingSchedulerClient = new SpecCachingSynchronousSchedulerClient(bucketSpecCacheSchedulerClient);
    final SpecFetcher specFetcher = new SpecFetcher(cachingSchedulerClient);

    writeToConfigRepository.setSpecFetcher(dockerImage -> Exceptions.toRuntime(() -> specFetcher.execute(dockerImage)));

    final SecretsMigration migration = new SecretsMigration(configs, readFromConfigRepository, writeToConfigRepository, false);
    LOGGER.info("starting: {}", SecretsMigration.class);
    migration.run();
    LOGGER.info("completed: {}", SecretsMigration.class);
  }

}
