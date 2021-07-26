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

package io.airbyte.migrate;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.enums.Enums;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

public class MigrationCurrentSchemaTest {

  // get all of the "current" configs (in other words the one airbyte-config). get all of the configs
  // from the output schema of the last migration. make sure they match.
  @Test
  void testConfigsOfLastMigrationMatchSource() {
    final Map<ResourceId, JsonNode> lastMigrationSchema = getSchemaOfLastMigration(ResourceType.CONFIG);
    final Map<ResourceId, JsonNode> currentSchema = MigrationUtils.getNameToSchemasFromResourcePath(
        Path.of("types"),
        ResourceType.CONFIG,
        Enums.valuesAsStrings(ConfigKeys.class));

    assertSameSchemas(currentSchema, lastMigrationSchema);
  }

  private static Map<ResourceId, JsonNode> getSchemaOfLastMigration(ResourceType resourceType) {
    final Migration lastMigration = Migrations.MIGRATIONS.get(Migrations.MIGRATIONS.size() - 1);
    final Map<ResourceId, JsonNode> lastMigrationOutputSchema = lastMigration.getOutputSchema();

    return lastMigrationOutputSchema.entrySet()
        .stream()
        .filter(entry -> entry.getKey().getType() == resourceType)
        .collect(Collectors.toMap(Entry::getKey, Entry::getValue));
  }

  // get all of the "current" jobs (in other words the one airbyte-db). get all of the configs
  // from the output schema of the last migration. make sure they match.
  @Test
  void testJobsOfLastMigrationMatchSource() {
    final Map<ResourceId, JsonNode> lastMigrationSchema = getSchemaOfLastMigration(ResourceType.JOB);
    final Map<ResourceId, JsonNode> currentSchema = MigrationUtils.getNameToSchemasFromResourcePath(
        Path.of("jobs_database"),
        ResourceType.JOB,
        Enums.valuesAsStrings(JobKeys.class));

    assertSameSchemas(currentSchema, lastMigrationSchema);
  }

  private static void assertSameSchemas(Map<ResourceId, JsonNode> currentSchemas, Map<ResourceId, JsonNode> lastMigrationSchema) {
    assertEquals(currentSchemas.size(), lastMigrationSchema.size());

    final List<Entry<ResourceId, JsonNode>> lastMigrationOutputSchemaCleanedSorted = lastMigrationSchema.entrySet()
        .stream()
        .sorted(Comparator.comparing((v) -> v.getKey().getType()))
        .collect(Collectors.toList());

    // break out element-wise assertion so it is easier to read any failed tests.
    for (Map.Entry<ResourceId, JsonNode> lastMigrationEntry : lastMigrationOutputSchemaCleanedSorted) {
      assertEquals(lastMigrationEntry.getValue(), currentSchemas.get(lastMigrationEntry.getKey()));
    }
  }

  public enum ConfigKeys {
    STANDARD_WORKSPACE,
    STANDARD_SOURCE_DEFINITION,
    STANDARD_DESTINATION_DEFINITION,
    SOURCE_CONNECTION,
    DESTINATION_CONNECTION,
    STANDARD_SYNC,
    STANDARD_SYNC_SCHEDULE,
    STANDARD_SYNC_OPERATION,
  }

  public enum JobKeys {
    JOBS,
    ATTEMPTS,
    AIRBYTE_METADATA
  }

}
