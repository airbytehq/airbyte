/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

public interface Migration {

  /**
   * The Airbyte Version associated with this migration. This string must be unique across all
   * migration. This string is never used as a sort key.
   *
   * @return version
   */
  String getVersion();

  /**
   * Returns a map of the relative path of the file resource within the input archive to the
   * JsonSchema associated with the records that will be received as input for this migration. If
   * records do not match these schemas, the migration will fail.
   *
   * @return map
   */
  Map<ResourceId, JsonNode> getInputSchema();

  /**
   * Returns a map of the relative path of the file resource within the output archive to the
   * JsonSchema associated with the records that will be output for this resource in migration. If
   * records do not match theses schemas, the migration will fail.
   *
   * @return map
   */
  Map<ResourceId, JsonNode> getOutputSchema();

  /**
   * Execute migration.
   *
   * @param inputData Map of the relative path of the file resource within the input archive to a
   *        stream of its records.
   * @param outputData Map of the relative path of the file resource within the output archive to a
   *        consumer that takes the transformed records.
   */
  void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData);

}
