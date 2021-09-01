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
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

/**
 * Unit test for the {@link DatabaseConfigPersistence#loadData} method.
 */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DatabaseConfigPersistenceLoadDataTest extends BaseDatabaseConfigPersistenceTest {

  private final ConfigPersistence seedPersistence = mock(ConfigPersistence.class);

  @BeforeAll
  public static void setup() throws Exception {
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DatabaseConfigPersistence(database));
    database.query(ctx -> ctx.execute("TRUNCATE TABLE airbyte_configs"));
  }

  @AfterAll
  public static void tearDown() throws Exception {
    database.close();
  }

  @BeforeEach
  public void resetPersistence() {
    reset(seedPersistence);
    reset(configPersistence);
  }

  @Test
  @Order(1)
  @DisplayName("When database is empty, seed should be copied to the database")
  public void testCopyConfigsToEmptyDatabase() throws Exception {
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
  }

  @Test
  @Order(2)
  @DisplayName("When database is not empty, configs should be updated")
  public void testUpdateConfigsInNonEmptyDatabase() throws Exception {
    // the seed has two destinations, one of which (S3) is new
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Lists.newArrayList(DESTINATION_S3, DESTINATION_SNOWFLAKE));

    configPersistence.loadData(seedPersistence);

    // the new destination is added
    assertRecordCount(3);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    verify(configPersistence, never()).copyConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
    verify(configPersistence, times(1)).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  @Test
  @Order(3)
  @DisplayName("When a connector is in use, its definition should not be updated")
  public void testNoUpdateForUsedConnector() throws Exception {
    // the seed has a newer version of s3 destination
    StandardDestinationDefinition destinationS3V2 = YamlSeedConfigPersistence.get()
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, "4816b78f-1489-44c1-9060-4b19d5fa9362", StandardDestinationDefinition.class)
        .withDockerImageTag("10000.1.0");
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Collections.singletonList(destinationS3V2));

    // create a sync to mark the destination as used
    StandardSync s3Sync = new StandardSync()
        .withSourceId(SOURCE_GITHUB.getSourceDefinitionId())
        .withDestinationId(destinationS3V2.getDestinationDefinitionId());
    configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC, UUID.randomUUID().toString(), s3Sync);

    configPersistence.loadData(seedPersistence);
    // s3 destination is not updated
    assertHasDestination(DESTINATION_S3);
  }

  @Test
  @Order(4)
  @DisplayName("When a connector is not in use, its definition should be updated")
  public void testUpdateForUnusedConnector() throws Exception {
    // the seed has a newer version of snowflake destination
    StandardDestinationDefinition snowflakeV2 = YamlSeedConfigPersistence.get()
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, "424892c4-daac-4491-b35d-c6688ba547ba", StandardDestinationDefinition.class)
        .withDockerImageTag("10000.2.0");
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Collections.singletonList(snowflakeV2));

    configPersistence.loadData(seedPersistence);
    assertHasDestination(snowflakeV2);
  }

}
