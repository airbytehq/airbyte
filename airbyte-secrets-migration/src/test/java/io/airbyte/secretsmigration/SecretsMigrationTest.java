/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.secretsmigration;

import static org.junit.Assert.fail;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.FileSystemConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

class SecretsMigrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SecretsMigrationTest.class);

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  public static final UUID UUID_1 = new UUID(0, 1);
  public static final StandardSourceDefinition SOURCE_1 = new StandardSourceDefinition();
  static final SourceConnection SOURCE_CONNECTION1;

  static {
    SOURCE_1.withSourceDefinitionId(UUID_1).withName("apache storm");
    SOURCE_CONNECTION1 = new SourceConnection().withSourceDefinitionId(SOURCE_1.getSourceDefinitionId()).withSourceId(UUID.randomUUID());
  }

  public static final UUID UUID_2 = new UUID(0, 2);
  public static final StandardSourceDefinition SOURCE_2 = new StandardSourceDefinition();
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests/");

  static {
    SOURCE_2.withSourceDefinitionId(UUID_2).withName("apache storm");
  }

  protected static PostgreSQLContainer<?> container;
  protected static Database database;
  private static EnvConfigs configs;
  private static ConfigPersistence readFromConfigPersistence;
  private static ConfigPersistence writeToConfigPersistence;
  private static Path rootPath;

  @BeforeAll
  static void init() throws IOException {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    readFromConfigPersistence = spy(new DatabaseConfigPersistence(database));
    rootPath = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), SecretsMigrationTest.class.getName());
    writeToConfigPersistence = new FileSystemConfigPersistence(rootPath);
  }

  @BeforeEach
  public void setup() throws Exception {
    configs = new EnvConfigs();
  }

  public static void failOnDifferingConfigurations(Map<String, Stream<JsonNode>> leftConfigs, Map<String, Stream<JsonNode>> rightConfigs) {
    // Check that both sets have exactly the same keys. If they don't, we already know we're failing the
    // diff.
    if (!leftConfigs.keySet().containsAll(rightConfigs.keySet()) && rightConfigs.keySet().containsAll(leftConfigs.keySet())) {
      fail("Configurations have different keys; cannot all match.");
    }
    // Now we know that the keys exactly match, so we can compare the values with a single pass,
    // presuming consistent ordering.
    for (String configSchemaName : leftConfigs.keySet()) {
      List<JsonNode> leftNodes = leftConfigs.get(configSchemaName).collect(Collectors.toList());
      List<JsonNode> rightNodes = rightConfigs.get(configSchemaName).collect(Collectors.toList());
      for (JsonNode left : leftNodes) {
        assertTrue(rightNodes.contains(left), "Missing left node from right collectin: " + left);
      }
      for (JsonNode right : rightNodes) {
        assertTrue(leftNodes.contains(right), "Missing right node from left collection: " + right);
      }
    }
  }

  /**
   * Ensure that we can read configs from the readFrom persistence, and save them out to the writeTo
   * persistence, via the ConfigRepository methods. This is the basic core workflow.
   */
  @Test
  public void exportImportTest() throws JsonValidationException, IOException {
    // setting up some arbitrary test data
    readFromConfigPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);
    readFromConfigPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_2.toString(), SOURCE_2);
    readFromConfigPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, SOURCE_CONNECTION1.getSourceId().toString(), SOURCE_CONNECTION1);

    // Set up more test data: configs of postgresql with ssl configurations and file source, and s3
    // destination;
    // make sure they have actual config in them, and that it comes through unharmed. This comes from
    // actual
    // json downloaded from our integration connectors.
    //
    // This ensures that for a variety of config shapes, we can either smoothly convert or we throw an
    // error when we can't.
    final StandardSourceDefinition FILE_SOURCE_DEF = Jsons.deserialize(MoreResources.readResource("file-source-config.json"),
        StandardSourceDefinition.class).withSourceDefinitionId(UUID.randomUUID());
    final StandardSourceDefinition POSTGRES_NOSSL_SOURCE_DEF = Jsons.deserialize(MoreResources.readResource("postgres-source-config-nossl.json"),
        StandardSourceDefinition.class).withSourceDefinitionId(UUID.randomUUID());
    final StandardSourceDefinition POSTGRES_SSL_SOURCE_DEF = Jsons.deserialize(MoreResources.readResource("postgres-source-config-ssl.json"),
        StandardSourceDefinition.class).withSourceDefinitionId(UUID.randomUUID());
    final StandardDestinationDefinition S3_DEST_DEF = Jsons.deserialize(MoreResources.readResource("s3-dest-config.json"),
        StandardDestinationDefinition.class).withDestinationDefinitionId(UUID.randomUUID());

    readFromConfigPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID.randomUUID().toString(), FILE_SOURCE_DEF);
    readFromConfigPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID.randomUUID().toString(), POSTGRES_NOSSL_SOURCE_DEF);
    readFromConfigPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID.randomUUID().toString(), POSTGRES_SSL_SOURCE_DEF);
    readFromConfigPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, UUID.randomUUID().toString(), S3_DEST_DEF);

    // Ensure that the dry run isn't modifying anything.
    assertTrue(writeToConfigPersistence.dumpConfigs().isEmpty(), "Write config should be empty before we use it (sanity check), but found keys: "
        + writeToConfigPersistence.dumpConfigs().keySet().toString());

    final SecretsMigration dryRunMigration = new SecretsMigration(configs, readFromConfigPersistence, writeToConfigPersistence, true);
    dryRunMigration.run();
    assertTrue(writeToConfigPersistence.dumpConfigs().isEmpty(), "Dry run should not have modified anything.");

    // real export-import
    final SecretsMigration migration = new SecretsMigration(configs, readFromConfigPersistence, writeToConfigPersistence, false);
    migration.run();

    // verify results
    assertEquals(
        Sets.newHashSet(SOURCE_1, SOURCE_2, FILE_SOURCE_DEF, POSTGRES_NOSSL_SOURCE_DEF, POSTGRES_SSL_SOURCE_DEF),
        Sets.newHashSet(writeToConfigPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)));

    assertEquals(
        Sets.newHashSet(SOURCE_CONNECTION1),
        Sets.newHashSet(writeToConfigPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)));

    failOnDifferingConfigurations(readFromConfigPersistence.dumpConfigs(), writeToConfigPersistence.dumpConfigs());
  }

  @AfterEach
  public void tearDown() {

  }

  @AfterAll
  static void cleanUp() {
    rootPath.toFile().delete();
  }

}
