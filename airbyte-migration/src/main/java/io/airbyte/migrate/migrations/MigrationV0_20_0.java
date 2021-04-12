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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This migration is currently empty and is a placeholder for migrations for the next 0.19.0 release
 *
 * Additionally, this migration updates the JSON Schema for StandardWorkspace with a new optional
 * field 'failureNotificationsWebhook' introduced in issue #1689
 */
public class MigrationV0_20_0 extends BaseMigration implements Migration {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationV0_20_0.class);

  private static final ResourceId STANDARD_WORKSPACE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_WORKSPACE");

  private static final String MIGRATION_VERSION = "0.20.0-alpha";

  private final Migration previousMigration;

  public MigrationV0_20_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getInputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(previousMigration.getOutputSchema());
    try {
      outputSchema.put(STANDARD_WORKSPACE_RESOURCE_ID,
          Jsons.jsonNode(MoreResources.readResource("migrations/migrationV0_20_0/StandardWorkspace.yaml")));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return outputSchema;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return getInputSchema();
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

      entry.getValue().forEach(r -> {
        // empty migration
        recordConsumer.accept(r);
      });
    }
  }

}
