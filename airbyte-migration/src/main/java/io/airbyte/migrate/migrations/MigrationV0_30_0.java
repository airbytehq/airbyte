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
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Migrates:
 * <ul>
 * <li>Slack/Webhook notification configuration to include flag for sending success notifications,
 * default to false.</li>
 * </ul>
 */
public class MigrationV0_30_0 extends BaseMigration implements Migration {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationV0_30_0.class);

  private static final Path RESOURCE_PATH = Path.of("migrations/migrationV0_30_0/airbyte_config");
  private static final String MIGRATION_VERSION = "0.30.0-alpha";

  private static final ResourceId WORKSPACE_RESOURCE_ID = ResourceId.fromConstantCase(
      ResourceType.CONFIG, "STANDARD_WORKSPACE");
  private final Migration previousMigration;

  public MigrationV0_30_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(
        previousMigration.getOutputSchema());
    outputSchema.put(WORKSPACE_RESOURCE_ID,
        MigrationUtils.getSchemaFromResourcePath(RESOURCE_PATH, WORKSPACE_RESOURCE_ID));
    return outputSchema;
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData,
                      Map<ResourceId, Consumer<JsonNode>> outputData) {

    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(r -> {
        if (entry.getKey().equals(WORKSPACE_RESOURCE_ID)) {
          if (r.hasNonNull("notifications")) {
            r.get("notifications").elements()
                .forEachRemaining(notification -> {
                  if ("slack".equals(notification.get("notificationType").asText(""))) {
                    JsonNode slackConfiguration = notification.get("slackConfiguration");
                    if (slackConfiguration != null) {
                      LOGGER.info(
                          "Adding sendOnSuccess=false, sendOnFailure=true for slack notification configuration");
                      ((ObjectNode) slackConfiguration).put("sendOnSuccess", false);
                      ((ObjectNode) slackConfiguration).put("sendOnFailure", true);
                    }
                  }
                });
          }
        }
        recordConsumer.accept(r);
      });
    }
  }

}
