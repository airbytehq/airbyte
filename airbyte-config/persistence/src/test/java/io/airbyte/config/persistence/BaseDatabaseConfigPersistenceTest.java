/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.count;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.ReleaseStage;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.Record1;
import org.jooq.Result;
import org.jooq.Table;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * This class provides downstream tests with constants and helpers.
 */
public abstract class BaseDatabaseConfigPersistenceTest {

  protected static PostgreSQLContainer<?> container;
  protected static Database database;
  protected static DatabaseConfigPersistence configPersistence;
  protected static JsonSecretsProcessor jsonSecretsProcessor;
  protected static DataSource dataSource;
  protected static DSLContext dslContext;
  protected static Flyway flyway;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    jsonSecretsProcessor = mock(JsonSecretsProcessor.class);
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  protected static void truncateAllTables() throws SQLException {
    database.query(ctx -> ctx
        .execute(
            "TRUNCATE TABLE workspace_service_account, state, actor_catalog, actor_catalog_fetch_event, connection_operation, connection, operation, actor_oauth_parameter, "
                + "actor, actor_definition, actor_definition_workspace_grant, workspace"));
  }

  protected static final StandardSourceDefinition SOURCE_GITHUB = new StandardSourceDefinition()
      .withName("GitHub")
      .withSourceDefinitionId(UUID.fromString("ef69ef6e-aa7f-4af1-a01d-ef775033524e"))
      .withDockerRepository("airbyte/source-github")
      .withDockerImageTag("0.2.3")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/github")
      .withIcon("github.svg")
      .withSourceType(SourceType.API)
      .withTombstone(false);
  protected static final StandardSourceDefinition SOURCE_POSTGRES = new StandardSourceDefinition()
      .withName("Postgres")
      .withSourceDefinitionId(UUID.fromString("decd338e-5647-4c0b-adf4-da0e75f5a750"))
      .withDockerRepository("airbyte/source-postgres")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withSourceType(SourceType.DATABASE)
      .withTombstone(false);
  protected static final StandardSourceDefinition SOURCE_CUSTOM = new StandardSourceDefinition()
      .withName("Custom")
      .withSourceDefinitionId(UUID.fromString("baba338e-5647-4c0b-adf4-da0e75f5a750"))
      .withDockerRepository("airbyte/cusom")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withSourceType(SourceType.DATABASE)
      .withCustom(true)
      .withReleaseStage(ReleaseStage.CUSTOM)
      .withTombstone(false);
  protected static final StandardDestinationDefinition DESTINATION_SNOWFLAKE = new StandardDestinationDefinition()
      .withName("Snowflake")
      .withDestinationDefinitionId(UUID.fromString("424892c4-daac-4491-b35d-c6688ba547ba"))
      .withDockerRepository("airbyte/destination-snowflake")
      .withDockerImageTag("0.3.16")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/destinations/snowflake")
      .withTombstone(false);
  protected static final StandardDestinationDefinition DESTINATION_S3 = new StandardDestinationDefinition()
      .withName("S3")
      .withDestinationDefinitionId(UUID.fromString("4816b78f-1489-44c1-9060-4b19d5fa9362"))
      .withDockerRepository("airbyte/destination-s3")
      .withDockerImageTag("0.1.12")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/destinations/s3")
      .withTombstone(false);
  protected static final StandardDestinationDefinition DESTINATION_CUSTOM = new StandardDestinationDefinition()
      .withName("Custom")
      .withDestinationDefinitionId(UUID.fromString("baba338e-5647-4c0b-adf4-da0e75f5a750"))
      .withDockerRepository("airbyte/cusom")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withCustom(true)
      .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM)
      .withTombstone(false);

  protected static void writeSource(final ConfigPersistence configPersistence, final StandardSourceDefinition source) throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(), source);
  }

  protected static void writeSourceWithSourceConnection(final ConfigPersistence configPersistence, final StandardSourceDefinition source)
      throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(), source);
    final UUID connectionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withName("can not be null")
        .withSlug("can not be null")
        .withInitialSetupComplete(true);
    configPersistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString(), workspace);

    final SourceConnection sourceConnection = new SourceConnection()
        .withSourceId(connectionId)
        .withWorkspaceId(workspaceId)
        .withName("can not be null")
        .withSourceDefinitionId(source.getSourceDefinitionId());
    configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, connectionId.toString(), sourceConnection);
  }

  protected static void writeDestination(final ConfigPersistence configPersistence, final StandardDestinationDefinition destination)
      throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(), destination);
  }

  protected static void writeDestinationWithDestinationConnection(final ConfigPersistence configPersistence,
                                                                  final StandardDestinationDefinition destination)
      throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(), destination);
    final UUID connectionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withName("can not be null")
        .withSlug("can not be null")
        .withInitialSetupComplete(true);
    configPersistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString(), workspace);

    final DestinationConnection destinationConnection = new DestinationConnection()
        .withDestinationId(connectionId)
        .withWorkspaceId(workspaceId)
        .withName("can not be null")
        .withDestinationDefinitionId(destination.getDestinationDefinitionId());
    configPersistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, connectionId.toString(), destinationConnection);
  }

  protected static void writeDestinations(final ConfigPersistence configPersistence, final List<StandardDestinationDefinition> destinations)
      throws Exception {
    final Map<String, StandardDestinationDefinition> destinationsByID = destinations.stream()
        .collect(Collectors.toMap(destinationDefinition -> destinationDefinition.getDestinationDefinitionId().toString(), Function.identity()));
    configPersistence.writeConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destinationsByID);
  }

  protected static void deleteDestination(final ConfigPersistence configPersistence, final StandardDestinationDefinition destination)
      throws Exception {
    configPersistence.deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString());
  }

  protected Map<String, Set<JsonNode>> getMapWithSet(final Map<String, Stream<JsonNode>> input) {
    return input.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        e -> e.getValue().collect(Collectors.toSet())));
  }

  // assertEquals cannot correctly check the equality of two maps with stream values,
  // so streams are converted to sets before being compared.
  protected void assertSameConfigDump(final Map<String, Stream<JsonNode>> expected, final Map<String, Stream<JsonNode>> actual) {
    assertEquals(getMapWithSet(expected), getMapWithSet(actual));
  }

  protected void assertRecordCount(final int expectedCount, final Table table) throws Exception {
    final Result<Record1<Integer>> recordCount = database.query(ctx -> ctx.select(count(asterisk())).from(table).fetch());
    assertEquals(expectedCount, recordCount.get(0).value1());
  }

  protected void assertHasSource(final StandardSourceDefinition source) throws Exception {
    assertEquals(source, configPersistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(),
            StandardSourceDefinition.class));
  }

  protected void assertHasDestination(final StandardDestinationDefinition destination) throws Exception {
    assertEquals(destination, configPersistence
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(),
            StandardDestinationDefinition.class));
  }

}
