/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

public class MigrationV0_27_0 extends BaseMigration implements Migration {

  protected static final ResourceId STANDARD_SYNC_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");

  private static final String MIGRATION_VERSION = "0.27.0-alpha";
  @VisibleForTesting
  protected final Migration previousMigration;

  public MigrationV0_27_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  private static final Path RESOURCE_PATH = Path.of("migrations/migrationV0_27_0/");

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(previousMigration.getOutputSchema());
    outputSchema.put(
        STANDARD_SYNC_RESOURCE_ID,
        MigrationUtils.getSchemaFromResourcePath(RESOURCE_PATH, STANDARD_SYNC_RESOURCE_ID));
    return outputSchema;
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData,
                      Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

      entry.getValue().forEach(r -> {
        // empty migration
        recordConsumer.accept(r);
      });
    }
  }

}
