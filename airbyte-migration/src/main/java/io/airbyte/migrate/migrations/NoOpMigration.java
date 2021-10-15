/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.ResourceId;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

/**
 * Placeholder migration for when the minor version changes but there were no schema changes for the
 * underlying data. In this scenario we just need to bump the versions in the data and move on.
 */
public class NoOpMigration extends BaseMigration implements Migration {

  private final String version;
  private final Migration previousMigration;

  public NoOpMigration(final Migration previousMigration, final String version) {
    super(previousMigration);
    this.previousMigration = previousMigration;
    this.version = version;
  }

  @Override
  public String getVersion() {
    return version;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return previousMigration.getOutputSchema();
  }

  @Override
  public void migrate(final Map<ResourceId, Stream<JsonNode>> inputData, final Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(recordConsumer);
    }
  }

}
