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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.DatabaseConfigPersistence.ConnectorInfo;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * The {@link DatabaseConfigPersistence#loadData} method is tested in
 * {@link DatabaseConfigPersistenceLoadDataTest}.
 */
public class DatabaseConfigPersistenceTest extends BaseDatabaseConfigPersistenceTest {

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

  @Test
  public void testGetConnectorRepositoryToInfoMap() throws Exception {
    String connectorRepository = "airbyte/duplicated-connector";
    String oldVersion = "0.1.10";
    String newVersion = "0.2.0";
    StandardSourceDefinition source1 = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withDockerRepository(connectorRepository)
        .withDockerImageTag(oldVersion);
    StandardSourceDefinition source2 = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withDockerRepository(connectorRepository)
        .withDockerImageTag(newVersion);
    writeSource(configPersistence, source1);
    writeSource(configPersistence, source2);
    Map<String, ConnectorInfo> result = database.query(ctx -> configPersistence.getConnectorRepositoryToInfoMap(ctx));
    // when there are duplicated connector definitions, the one with the latest version should be
    // retrieved
    assertEquals(newVersion, result.get(connectorRepository).dockerImageTag);
  }

  @Test
  public void testInsertConfigRecord() throws Exception {
    OffsetDateTime timestamp = OffsetDateTime.now();
    UUID definitionId = UUID.randomUUID();
    String connectorRepository = "airbyte/test-connector";

    // when the record does not exist, it is inserted
    StandardSourceDefinition source1 = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.2");
    int insertionCount = database.query(ctx -> configPersistence.insertConfigRecord(
        ctx,
        timestamp,
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        Jsons.jsonNode(source1),
        ConfigSchema.STANDARD_SOURCE_DEFINITION.getIdFieldName()));
    assertEquals(1, insertionCount);
    // write an irrelevant source to make sure that it is not changed
    writeSource(configPersistence, SOURCE_GITHUB);
    assertRecordCount(2);
    assertHasSource(source1);
    assertHasSource(SOURCE_GITHUB);

    // when the record already exists, it is ignored
    StandardSourceDefinition source2 = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.5");
    insertionCount = database.query(ctx -> configPersistence.insertConfigRecord(
        ctx,
        timestamp,
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        Jsons.jsonNode(source2),
        ConfigSchema.STANDARD_SOURCE_DEFINITION.getIdFieldName()));
    assertEquals(0, insertionCount);
    assertRecordCount(2);
    assertHasSource(source1);
    assertHasSource(SOURCE_GITHUB);
  }

  @Test
  public void testUpdateConfigRecord() throws Exception {
    OffsetDateTime timestamp = OffsetDateTime.now();
    UUID definitionId = UUID.randomUUID();
    String connectorRepository = "airbyte/test-connector";

    StandardSourceDefinition oldSource = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.3.5");
    writeSource(configPersistence, oldSource);
    // write an irrelevant source to make sure that it is not changed
    writeSource(configPersistence, SOURCE_GITHUB);
    assertRecordCount(2);
    assertHasSource(oldSource);
    assertHasSource(SOURCE_GITHUB);

    StandardSourceDefinition newSource = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.3.5");
    database.query(ctx -> configPersistence.updateConfigRecord(
        ctx,
        timestamp,
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        Jsons.jsonNode(newSource),
        definitionId.toString()));
    assertRecordCount(2);
    assertHasSource(newSource);
    assertHasSource(SOURCE_GITHUB);
  }

}
