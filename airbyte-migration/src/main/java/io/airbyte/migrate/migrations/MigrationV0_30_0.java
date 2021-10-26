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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This migration adds the StandardSyncState in the migration resource.
 */
public class MigrationV0_30_0 extends BaseMigration implements Migration {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationV0_30_0.class);
  private static final String MIGRATION_VERSION = "0.30.0-alpha";

  private static final Path RESOURCE_PATH = Path.of("migrations/migrationV0_30_0/airbyte_config");

  @VisibleForTesting
  protected static final ResourceId STANDARD_SYNC_STATE_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC_STATE");

  private final Migration previousMigration;

  public MigrationV0_30_0(final Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(previousMigration.getOutputSchema());
    outputSchema.put(STANDARD_SYNC_STATE_RESOURCE_ID,
        MigrationUtils.getSchemaFromResourcePath(RESOURCE_PATH, STANDARD_SYNC_STATE_RESOURCE_ID));
    return outputSchema;
  }

  // no op migration.
  @Override
  public void migrate(final Map<ResourceId, Stream<JsonNode>> inputData, final Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(recordConsumer);
    }
  }

}
