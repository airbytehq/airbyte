/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.secretsmigration;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.FileSystemConfigPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
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
  final Configs configs;
  final boolean dryRun;
  final ConfigPersistence readFromPersistence;
  final ConfigPersistence writeToPersistence;

  public SecretsMigration(Configs envConfigs, ConfigPersistence readFromPersistence, ConfigPersistence writeToPersistence, boolean dryRun) {
    this.configs = envConfigs;
    this.readFromPersistence = readFromPersistence;
    this.writeToPersistence = writeToPersistence;
    this.dryRun = dryRun;
  }

  public void run() throws IOException {
    LOGGER.info("Starting migration run.");

    final ConfigRepository readFromConfigRepository =
        new ConfigRepository(readFromPersistence, new NoOpSecretsHydrator(), Optional.empty(), Optional.empty());
    final ConfigRepository writeToConfigRepository =
        new ConfigRepository(writeToPersistence, new NoOpSecretsHydrator(), Optional.empty(), Optional.empty());

    LOGGER.info("... Dry Run: deserializing configurations and writing to the new store...");
    Map<String, Stream<JsonNode>> configurations = readFromConfigRepository.dumpConfigs();
    writeToConfigRepository.replaceAllConfigsDeserializing(configurations, true);

    LOGGER.info("... With dryRun=" + dryRun + ": deserializing configurations and writing to the new store...");
    configurations = readFromConfigRepository.dumpConfigs();
    writeToConfigRepository.replaceAllConfigsDeserializing(configurations, dryRun);

    LOGGER.info("Migration run complete.");
  }

  public static void main(String[] args) throws Exception {
    final Configs configs = new EnvConfigs();
    final ConfigPersistence readFromPersistence = new DatabaseConfigPersistence(new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized()).withValidation();
    final ConfigPersistence writeToPersistence = new FileSystemConfigPersistence(TEST_ROOT);
    final SecretsMigration migration = new SecretsMigration(configs, readFromPersistence, writeToPersistence, false);
    LOGGER.info("starting: {}", SecretsMigration.class);
    migration.run();
    LOGGER.info("completed: {}", SecretsMigration.class);
  }

}
