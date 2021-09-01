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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.db.Database;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.Record1;
import org.jooq.Result;
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

  protected static final StandardSourceDefinition SOURCE_GITHUB;
  protected static final StandardSourceDefinition SOURCE_POSTGRES;
  protected static final StandardDestinationDefinition DESTINATION_SNOWFLAKE;
  protected static final StandardDestinationDefinition DESTINATION_S3;

  static {
    try {
      ConfigPersistence seedPersistence = YamlSeedConfigPersistence.get();
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

  protected static void writeSource(ConfigPersistence configPersistence, StandardSourceDefinition source) throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(), source);
  }

  protected static void writeDestination(ConfigPersistence configPersistence, StandardDestinationDefinition destination) throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(), destination);
  }

  protected static void deleteDestination(ConfigPersistence configPersistence, StandardDestinationDefinition destination) throws Exception {
    configPersistence.deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString());
  }

  protected Map<String, Set<JsonNode>> getMapWithSet(Map<String, Stream<JsonNode>> input) {
    return input.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        e -> e.getValue().collect(Collectors.toSet())));
  }

  // assertEquals cannot correctly check the equality of two maps with stream values,
  // so streams are converted to sets before being compared.
  protected void assertSameConfigDump(Map<String, Stream<JsonNode>> expected, Map<String, Stream<JsonNode>> actual) {
    assertEquals(getMapWithSet(expected), getMapWithSet(actual));
  }

  protected void assertRecordCount(int expectedCount) throws Exception {
    Result<Record1<Integer>> recordCount = database.query(ctx -> ctx.select(count(asterisk())).from(table("airbyte_configs")).fetch());
    assertEquals(expectedCount, recordCount.get(0).value1());
  }

  protected void assertHasSource(StandardSourceDefinition source) throws Exception {
    assertEquals(source, configPersistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(),
            StandardSourceDefinition.class));
  }

  protected void assertHasDestination(StandardDestinationDefinition destination) throws Exception {
    assertEquals(destination, configPersistence
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(),
            StandardDestinationDefinition.class));
  }

}
