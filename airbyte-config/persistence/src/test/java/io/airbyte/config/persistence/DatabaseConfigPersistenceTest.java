/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.persistence.AirbyteConfigsTable.AIRBYTE_CONFIGS;
import static io.airbyte.config.persistence.AirbyteConfigsTable.AIRBYTE_CONFIGS_TABLE_SCHEMA;
import static io.airbyte.config.persistence.AirbyteConfigsTable.CONFIG_BLOB;
import static io.airbyte.config.persistence.AirbyteConfigsTable.CONFIG_ID;
import static io.airbyte.config.persistence.AirbyteConfigsTable.CONFIG_TYPE;
import static io.airbyte.config.persistence.AirbyteConfigsTable.CREATED_AT;
import static io.airbyte.config.persistence.AirbyteConfigsTable.UPDATED_AT;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.count;
import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.JSONB;
import org.jooq.Record1;
import org.jooq.Result;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class DatabaseConfigPersistenceTest {

  private static PostgreSQLContainer<?> container;

  private static final StandardWorkspace WORKSPACE;
  private static final StandardSourceDefinition SOURCE_GITHUB;
  private static final StandardSourceDefinition SOURCE_POSTGRES;
  private static final StandardDestinationDefinition DESTINATION_SNOWFLAKE;
  private static final StandardDestinationDefinition DESTINATION_S3;

  static {
    try {
      ConfigPersistence seedPersistence = new YamlSeedConfigPersistence();
      WORKSPACE = seedPersistence
          .getConfig(ConfigSchema.STANDARD_WORKSPACE, PersistenceConstants.DEFAULT_WORKSPACE_ID.toString(), StandardWorkspace.class);
      SOURCE_GITHUB = seedPersistence
          .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, "ef69ef6e-aa7f-4af1-a01d-ef775033524e", StandardSourceDefinition.class);
      SOURCE_POSTGRES = seedPersistence
          .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, "decd338e-5647-4c0b-adf4-da0e75f5a750", StandardSourceDefinition.class);
      DESTINATION_SNOWFLAKE = seedPersistence
          .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, "424892c4-daac-4491-b35d-c6688ba547ba", StandardDestinationDefinition.class);
      DESTINATION_S3 = seedPersistence
          .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, "4816b78f-1489-44c1-9060-4b19d5fa9362", StandardDestinationDefinition.class);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  private Database database;
  private DatabaseConfigPersistence configPersistence;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @BeforeEach
  public void setup() throws Exception {
    database = Databases.createPostgresDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
    configPersistence = new DatabaseConfigPersistence(database);
    configPersistence.initialize(MoreResources.readResource(AIRBYTE_CONFIGS_TABLE_SCHEMA));
    database.query(ctx -> ctx.execute("TRUNCATE TABLE airbyte_configs"));
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  @Test
  public void testInitialize() throws SQLException {
    // check table
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS)));
    // check columns (if any of the column does not exist, the query will throw exception)
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_ID.eq("ID"))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_TYPE.eq("TYPE"))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_BLOB.eq(JSONB.valueOf("{}")))));
    Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CREATED_AT.eq(timestamp))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(UPDATED_AT.eq(timestamp))));
  }

  @Test
  public void testLoadData() throws Exception {
    ConfigPersistence seedPersistence = mock(ConfigPersistence.class);
    Map<String, Stream<JsonNode>> seeds = Map.of(
        ConfigSchema.STANDARD_WORKSPACE.name(), Stream.of(Jsons.jsonNode(WORKSPACE)),
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), Stream.of(Jsons.jsonNode(SOURCE_GITHUB), Jsons.jsonNode(SOURCE_POSTGRES)),
        ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(), Stream.of(Jsons.jsonNode(DESTINATION_S3)));
    when(seedPersistence.dumpConfigs()).thenReturn(seeds);

    configPersistence.loadData(seedPersistence);

    assertRecordCount(4);
    assertHasWorkspace(WORKSPACE);
    assertHasSource(SOURCE_GITHUB);
    assertHasSource(SOURCE_POSTGRES);
    assertHasDestination(DESTINATION_S3);
  }

  @Test
  public void testWriteAndGetConfig() throws Exception {
    writeDestination(DESTINATION_S3);
    writeDestination(DESTINATION_SNOWFLAKE);
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3),
        configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
  }

  @Test
  public void testReplaceAllConfigs() throws Exception {
    writeDestination(DESTINATION_S3);
    writeDestination(DESTINATION_SNOWFLAKE);

    Map<ConfigSchema, Stream<Object>> newConfigs = Map.of(
        ConfigSchema.STANDARD_WORKSPACE, Stream.of(WORKSPACE),
        ConfigSchema.STANDARD_SOURCE_DEFINITION, Stream.of(SOURCE_GITHUB, SOURCE_POSTGRES));

    configPersistence.replaceAllConfigs(newConfigs, true);

    // dry run does not change anything
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    configPersistence.replaceAllConfigs(newConfigs, false);
    assertRecordCount(3);
    assertHasWorkspace(WORKSPACE);
    assertHasSource(SOURCE_GITHUB);
    assertHasSource(SOURCE_POSTGRES);
  }

  @Test
  public void testDumpConfigs() throws Exception {
    writeSource(SOURCE_GITHUB);
    writeSource(SOURCE_POSTGRES);
    writeDestination(DESTINATION_S3);
    Map<String, Stream<JsonNode>> actual = configPersistence.dumpConfigs();
    Map<String, Stream<JsonNode>> expected = Map.of(
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), Stream.of(Jsons.jsonNode(SOURCE_GITHUB), Jsons.jsonNode(SOURCE_POSTGRES)),
        ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(), Stream.of(Jsons.jsonNode(DESTINATION_S3)));
    assertEquals(getMapWithSet(expected), getMapWithSet(actual));
  }

  // assertEquals cannot correctly check the equality of two maps with stream values,
  // so streams are converted to sets
  private Map<String, Set<JsonNode>> getMapWithSet(Map<String, Stream<JsonNode>> input) {
    return input.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        e -> e.getValue().collect(Collectors.toSet())));
  }

  private void writeSource(StandardSourceDefinition source) throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(), source);
  }

  private void writeDestination(StandardDestinationDefinition destination) throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(), destination);
  }

  private void assertRecordCount(int expectedCount) throws Exception {
    Result<Record1<Integer>> recordCount = database.query(ctx -> ctx.select(count(asterisk())).from(AIRBYTE_CONFIGS).fetch());
    assertEquals(expectedCount, recordCount.get(0).value1());
  }

  private void assertHasWorkspace(StandardWorkspace workspace) throws Exception {
    assertEquals(workspace,
        configPersistence.getConfig(ConfigSchema.STANDARD_WORKSPACE, workspace.getWorkspaceId().toString(), StandardWorkspace.class));
  }

  private void assertHasSource(StandardSourceDefinition source) throws Exception {
    assertEquals(source, configPersistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(),
            StandardSourceDefinition.class));
  }

  private void assertHasDestination(StandardDestinationDefinition destination) throws Exception {
    assertEquals(destination, configPersistence
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(),
            StandardDestinationDefinition.class));
  }
}
