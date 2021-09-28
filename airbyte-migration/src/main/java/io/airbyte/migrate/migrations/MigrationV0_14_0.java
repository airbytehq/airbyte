/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Suppliers;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.stream.Stream;

/**
 * This migration is a bit of an outlier. As the first migration we just use it certify the schema
 * we expect to be present at the start of history.
 */
public class MigrationV0_14_0 implements Migration {

  private static final Path RESOURCE_PATH = Path.of("migrations/migrationV0_14_0");
  private final Supplier<Map<ResourceId, JsonNode>> outputSchemaSupplier;

  public MigrationV0_14_0() {
    // avoid pulling schema from disk multiple times. calling getOutputSchema should be cheap.
    outputSchemaSupplier = Suppliers.memoize(() -> MoreMaps.merge(
        MigrationUtils.getConfigModels(RESOURCE_PATH, Enums.valuesAsStrings(ConfigKeys.class)),
        MigrationUtils.getJobModels(RESOURCE_PATH, Enums.valuesAsStrings(JobKeys.class))));
  }

  @Override
  public String getVersion() {
    return "0.14.0-alpha";
  }

  @Override
  public Map<ResourceId, JsonNode> getInputSchema() {
    return Collections.emptyMap();
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return outputSchemaSupplier.get();
  }

  // no op migration.
  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(recordConsumer);
    }
  }

  public enum ConfigKeys {
    STANDARD_WORKSPACE,
    STANDARD_SOURCE_DEFINITION,
    STANDARD_DESTINATION_DEFINITION,
    SOURCE_CONNECTION,
    DESTINATION_CONNECTION,
    STANDARD_SYNC,
    STANDARD_SYNC_SCHEDULE
  }

  public enum JobKeys {
    JOBS,
    ATTEMPTS,
    AIRBYTE_METADATA
  }

}
