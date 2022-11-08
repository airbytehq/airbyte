/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.DatabaseConfigPersistence.ConnectorInfo;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit test for the {@link DatabaseConfigPersistence#updateConnectorDefinitions} method.
 */
@SuppressWarnings("PMD.SignatureDeclareThrowsException")
class DatabaseConfigPersistenceUpdateConnectorDefinitionsTest extends BaseDatabaseConfigPersistenceTest {

  private static final JsonNode SOURCE_GITHUB_JSON = Jsons.jsonNode(SOURCE_GITHUB);
  private static final String DOCKER_IMAGE_TAG = "0.0.0";
  private static final String DOCKER_IMAGE_TAG_2 = "0.1000.0";
  private static final String DEFAULT_PROTOCOL_VERSION = "0.2.0";

  @BeforeAll
  public static void setup() throws Exception {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    flyway = FlywayFactory.create(dataSource, DatabaseConfigPersistenceUpdateConnectorDefinitionsTest.class.getName(),
        ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    database = new ConfigsDatabaseTestProvider(dslContext, flyway).create(false);
    configPersistence = new DatabaseConfigPersistence(database);
    final ConfigsDatabaseMigrator configsDatabaseMigrator =
        new ConfigsDatabaseMigrator(database, flyway);
    final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(configsDatabaseMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
  }

  @AfterAll
  public static void tearDown() throws Exception {
    dslContext.close();
    DataSourceFactory.close(dataSource);
  }

  @BeforeEach
  public void resetDatabase() throws SQLException {
    truncateAllTables();
  }

  @Test
  @DisplayName("When a connector does not exist, add it")
  void testNewConnector() throws Exception {
    final StandardSourceDefinition expectedSourceDef = cloneWithProtocolVersion(SOURCE_GITHUB, DEFAULT_PROTOCOL_VERSION);
    assertUpdateConnectorDefinition(
        Collections.emptyList(),
        Collections.emptyList(),
        List.of(SOURCE_GITHUB),
        Collections.singletonList(expectedSourceDef));
  }

  @Test
  @DisplayName("When an old connector is in use, if it has all fields, do not update it")
  void testOldConnectorInUseWithAllFields() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag(DOCKER_IMAGE_TAG);
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag(DOCKER_IMAGE_TAG_2);

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(currentSource));
  }

  @Test
  @DisplayName("When a old connector is in use, add missing fields, do not update its version")
  void testOldConnectorInUseWithMissingFields() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag(DOCKER_IMAGE_TAG).withDocumentationUrl(null).withSourceType(null);
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag(DOCKER_IMAGE_TAG_2);
    final StandardSourceDefinition currentSourceWithNewFields = getSource().withDockerImageTag(DOCKER_IMAGE_TAG);
    final StandardSourceDefinition expectedSourceDef = cloneWithProtocolVersion(currentSourceWithNewFields, DEFAULT_PROTOCOL_VERSION);

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(expectedSourceDef));
  }

  @Test
  @DisplayName("When a old connector is in use and there is a new patch version, update its version")
  void testOldConnectorInUseWithMinorVersion() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.1.0");
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.1.9");
    final StandardSourceDefinition expectedSourceDef = cloneWithProtocolVersion(latestSource, DEFAULT_PROTOCOL_VERSION);

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(expectedSourceDef));
  }

  @Test
  @DisplayName("When a old connector is in use and there is a new minor version, do not update its version")
  void testOldConnectorInUseWithPathVersion() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.1.0");
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.2.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(currentSource));
  }

  @Test
  @DisplayName("When an unused connector has a new version, update it")
  void testUnusedConnectorWithOldVersion() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag(DOCKER_IMAGE_TAG);
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag(DOCKER_IMAGE_TAG_2);
    final String protocolVersion = "1.0.3";
    latestSource.withSpec(new ConnectorSpecification().withProtocolVersion(protocolVersion));
    final StandardSourceDefinition expectedSourceDef = cloneWithProtocolVersion(latestSource, protocolVersion);

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.emptyList(),
        Collections.singletonList(latestSource),
        Collections.singletonList(expectedSourceDef));
  }

  @Test
  @DisplayName("When an unused connector has missing fields, add the missing fields, do not update its version")
  void testUnusedConnectorWithMissingFields() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag(DOCKER_IMAGE_TAG_2).withDocumentationUrl(null).withSourceType(null);
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.99.0");
    final StandardSourceDefinition currentSourceWithNewFields = getSource().withDockerImageTag(DOCKER_IMAGE_TAG_2);
    final StandardSourceDefinition expectedSourceDef = cloneWithProtocolVersion(currentSourceWithNewFields, DEFAULT_PROTOCOL_VERSION);

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.emptyList(),
        Collections.singletonList(latestSource),
        Collections.singletonList(expectedSourceDef));
  }

  /**
   * Clone a source for modification and testing.
   */
  private StandardSourceDefinition getSource() {
    return Jsons.object(Jsons.clone(SOURCE_GITHUB_JSON), StandardSourceDefinition.class);
  }

  private StandardSourceDefinition cloneWithProtocolVersion(final StandardSourceDefinition sourceDef, final String protocolVersion) {
    final StandardSourceDefinition clonedDef = Jsons.deserialize(Jsons.serialize(sourceDef), StandardSourceDefinition.class);
    clonedDef.withProtocolVersion(protocolVersion);
    return clonedDef;
  }

  /**
   * @param currentSources all sources currently exist in the database
   * @param currentSourcesInUse a subset of currentSources; sources currently used in data syncing
   */
  private void assertUpdateConnectorDefinition(final List<StandardSourceDefinition> currentSources,
                                               final List<StandardSourceDefinition> currentSourcesInUse,
                                               final List<StandardSourceDefinition> latestSources,
                                               final List<StandardSourceDefinition> expectedUpdatedSources)
      throws Exception {
    for (final StandardSourceDefinition source : currentSources) {
      writeSource(configPersistence, source);
    }

    for (final StandardSourceDefinition source : currentSourcesInUse) {
      assertTrue(currentSources.contains(source), "currentSourcesInUse must exist in currentSources");
    }

    final Set<String> sourceRepositoriesInUse = currentSourcesInUse.stream()
        .map(StandardSourceDefinition::getDockerRepository)
        .collect(Collectors.toSet());
    final Map<String, ConnectorInfo> currentSourceRepositoryToInfo = currentSources.stream()
        .collect(Collectors.toMap(
            StandardSourceDefinition::getDockerRepository,
            s -> new ConnectorInfo(s.getSourceDefinitionId().toString(), Jsons.jsonNode(s))));

    database.transaction(ctx -> {
      try {
        configPersistence.updateConnectorDefinitions(
            ctx,
            ConfigSchema.STANDARD_SOURCE_DEFINITION,
            latestSources,
            sourceRepositoriesInUse,
            currentSourceRepositoryToInfo);
      } catch (final IOException e) {
        throw new SQLException(e);
      }
      return null;
    });

    assertRecordCount(expectedUpdatedSources.size(), ACTOR_DEFINITION);
    for (final StandardSourceDefinition source : expectedUpdatedSources) {
      assertHasSource(source);
    }
  }

}
