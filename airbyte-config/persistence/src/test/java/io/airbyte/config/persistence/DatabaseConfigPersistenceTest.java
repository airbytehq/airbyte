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

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.count;
import static org.jooq.impl.DSL.table;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.Record1;
import org.jooq.Result;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class DatabaseConfigPersistenceTest extends BaseTest {

  private static PostgreSQLContainer<?> container;

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
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DatabaseConfigPersistence(database));
    database.query(ctx -> ctx.execute("TRUNCATE TABLE airbyte_configs"));
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  @Test
  public void testLoadData() throws Exception {
    // 1. when the database is empty, seed will be copied into the database
    ConfigPersistence seedPersistence = mock(ConfigPersistence.class);
    Map<String, Stream<JsonNode>> initialSeeds = Map.of(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(), Stream.of(Jsons.jsonNode(DESTINATION_SNOWFLAKE)),
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), Stream.of(Jsons.jsonNode(SOURCE_GITHUB)));
    when(seedPersistence.dumpConfigs()).thenReturn(initialSeeds);

    configPersistence.loadData(seedPersistence);
    assertRecordCount(2);
    assertHasSource(SOURCE_GITHUB);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    verify(configPersistence, times(1)).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    verify(configPersistence, never()).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));

    // 2. when the database is not empty, configs will be updated
    // the seed has two destinations, one of which (S3) is new
    reset(seedPersistence);
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Lists.newArrayList(DESTINATION_S3, DESTINATION_SNOWFLAKE));

    reset(configPersistence);
    configPersistence.loadData(seedPersistence);
    assertRecordCount(3);
    assertHasSource(SOURCE_GITHUB);
    // the new destination is added
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    verify(configPersistence, never()).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    verify(configPersistence, times(1)).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));

    // 3. when a connector is used, its definition will not be updated
    // the seed has a newer version of s3 destination
    StandardDestinationDefinition destinationS3V2 = YamlSeedConfigPersistence.get()
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, "4816b78f-1489-44c1-9060-4b19d5fa9362", StandardDestinationDefinition.class)
        .withDockerImageTag("10000.1.0");
    reset(seedPersistence);
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Collections.singletonList(destinationS3V2));

    reset(configPersistence);
    StandardSync s3Sync = new StandardSync()
        .withSourceId(SOURCE_GITHUB.getSourceDefinitionId())
        .withDestinationId(destinationS3V2.getDestinationDefinitionId());
    configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC, UUID.randomUUID().toString(), s3Sync);
    configPersistence.loadData(seedPersistence);
    // s3 destination is not updated
    verify(configPersistence, never())
        .updateConfigRecord(any(DSLContext.class), any(OffsetDateTime.class), any(String.class), any(JsonNode.class), any(String.class));
    assertHasDestination(DESTINATION_S3);

    // 4. when a connector is not used, its definition will be updated
    // the seed has a newer version of snowflake destination
    StandardDestinationDefinition snowflakeV2 = YamlSeedConfigPersistence.get()
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, "424892c4-daac-4491-b35d-c6688ba547ba", StandardDestinationDefinition.class)
        .withDockerImageTag("10000.2.0");
    reset(seedPersistence);
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Collections.singletonList(snowflakeV2));

    reset(configPersistence);
    configPersistence.loadData(seedPersistence);
    // snowflake destination is updated
    verify(configPersistence, times(1))
        .updateConfigRecord(any(DSLContext.class), any(OffsetDateTime.class), any(String.class), any(JsonNode.class), any(String.class));
    assertHasDestination(snowflakeV2);
  }

  @Test
  public void testWriteAndGetConfig() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3),
        configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
  }

  @Test
  public void testDeleteConfig() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3),
        configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
    deleteDestination(configPersistence, DESTINATION_S3);
    assertThrows(ConfigNotFoundException.class, () -> assertHasDestination(DESTINATION_S3));
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE),
        configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
  }

  @Test
  public void testReplaceAllConfigs() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);

    final Map<AirbyteConfig, Stream<Object>> newConfigs = Map.of(ConfigSchema.STANDARD_SOURCE_DEFINITION, Stream.of(SOURCE_GITHUB, SOURCE_POSTGRES));

    configPersistence.replaceAllConfigs(newConfigs, true);

    // dry run does not change anything
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    configPersistence.replaceAllConfigs(newConfigs, false);
    assertRecordCount(2);
    assertHasSource(SOURCE_GITHUB);
    assertHasSource(SOURCE_POSTGRES);
  }

  @Test
  public void testDumpConfigs() throws Exception {
    writeSource(configPersistence, SOURCE_GITHUB);
    writeSource(configPersistence, SOURCE_POSTGRES);
    writeDestination(configPersistence, DESTINATION_S3);
    Map<String, Stream<JsonNode>> actual = configPersistence.dumpConfigs();
    Map<String, Stream<JsonNode>> expected = Map.of(
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), Stream.of(Jsons.jsonNode(SOURCE_GITHUB), Jsons.jsonNode(SOURCE_POSTGRES)),
        ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(), Stream.of(Jsons.jsonNode(DESTINATION_S3)));
    assertSameConfigDump(expected, actual);
  }

  private void assertRecordCount(int expectedCount) throws Exception {
    Result<Record1<Integer>> recordCount = database.query(ctx -> ctx.select(count(asterisk())).from(table("airbyte_configs")).fetch());
    assertEquals(expectedCount, recordCount.get(0).value1());
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
