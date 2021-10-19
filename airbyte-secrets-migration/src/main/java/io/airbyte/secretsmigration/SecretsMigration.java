/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.secretsmigration;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.LocalTestingSecretPersistence;
import io.airbyte.config.persistence.split_secrets.RealSecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.scheduler.client.BucketSpecCacheSchedulerClient;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SecretsMigration {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final Logger LOGGER = LoggerFactory.getLogger(SecretsMigration.class);
  final boolean dryRun;
  final ConfigRepository readFrom;
  final ConfigRepository writeTo;

  public SecretsMigration(final ConfigRepository readFrom, final ConfigRepository writeTo, final boolean dryRun) {
    this.readFrom = readFrom;
    this.writeTo = writeTo;
    this.dryRun = dryRun;
  }

  public void run() throws IOException {
    LOGGER.info("Starting migration run.");

    LOGGER.info("... Dry Run: deserializing configurations and writing to the new store...");
    Map<String, Stream<JsonNode>> configurations = readFrom.dumpConfigs();
    writeTo.replaceAllConfigsDeserializing(configurations, true);

    LOGGER.info("... With dryRun=" + dryRun + ": deserializing configurations and writing to the new store...");
    configurations = readFrom.dumpConfigs();
    writeTo.replaceAllConfigsDeserializing(configurations, dryRun);

    LOGGER.info("Migration run complete.");
  }

  public static void main(final String[] args) throws Exception {
    final Configs configs = new EnvConfigs();

    final Database database = new ConfigsDatabaseInstance(
        "docker", // configs.getConfigDatabaseUser(),
        "docker", // configs.getConfigDatabasePassword(),
        "jdbc:postgresql://localhost:8011/airbyte") // configs.getConfigDatabaseUrl())
            .getInitialized();

    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(database).withValidation();

    final ConfigRepository configRepository =
        new ConfigRepository(
            configPersistence,
            new RealSecretsHydrator(new LocalTestingSecretPersistence(database)),
            Optional.of(new LocalTestingSecretPersistence(database)),
            Optional.of(new LocalTestingSecretPersistence(database)));

    configRepository.setSpecFetcher(dockerImage -> BucketSpecCacheSchedulerClient
        .attemptToFetchSpecFromBucket(StorageOptions.getDefaultInstance().getService(), "io-airbyte-cloud-spec-cache", dockerImage).get());

    final SecretsMigration migration = new SecretsMigration(configRepository, configRepository, false);
    LOGGER.info("starting: {}", SecretsMigration.class);
    migration.run();
    LOGGER.info("completed: {}", SecretsMigration.class);
  }

}
