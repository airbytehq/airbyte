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

package io.airbyte.migrate.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationTestUtils;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.Migrations;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class MigrateV0_18_0Test {

  private static final ResourceId WORKSPACE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_WORKSPACE");

  @Test
  void testMigration() throws IOException {
    final JsonNode inputWorkspace = Jsons.jsonNode(ImmutableMap.<String, Object>builder()
        .put("workspaceId", "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6")
        .put("customerId", "6c56359e-4790-49fb-b0fb-28be70d218c2")
        .put("name", "default")
        .put("slug", "default")
        .put("initialSetupComplete", new Boolean(true))
        .put("anonymousDataCollection", new Boolean(false))
        .put("news", new Boolean(false))
        .put("securityUpdates", new Boolean(false))
        .put("displaySetupWizard", new Boolean(false))
        .build());

    final JsonNode outputWorkspace = Jsons.clone(inputWorkspace);
    ((ObjectNode) outputWorkspace).set("tombstone", BooleanNode.valueOf(false));

    final Map<ResourceId, Stream<JsonNode>> records = ImmutableMap.of(WORKSPACE_RESOURCE_ID, Stream.of(inputWorkspace));

    final Migration migration = Migrations.MIGRATIONS
        .stream()
        .filter(m -> m instanceof MigrationV0_18_0)
        .findAny()
        .orElse(null);
    assertNotNull(migration);

    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils.createOutputConsumer(migration.getOutputSchema().keySet());
    migration.migrate(records, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap.of(WORKSPACE_RESOURCE_ID, ImmutableList.of(outputWorkspace));
    final Map<ResourceId, List<JsonNode>> expectedOutput =
        MigrationTestUtils.createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils.collectConsumersToList(outputConsumer);
    assertEquals(expectedOutput, outputAsList);
  }

}
