/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;

/**
 * Helper methods for unit tests. This is needed by multiple modules, so it is in the src directory.
 */
public class AvroRecordHelper {

  public static JsonFieldNameUpdater getFieldNameUpdater(String streamName, String namespace, JsonNode streamSchema) {
    JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
    schemaConverter.getAvroSchema(streamSchema, streamName, namespace, true);
    return new JsonFieldNameUpdater(schemaConverter.getStandardizedNames());
  }

  /**
   * Convert an Airbyte JsonNode from Avro / Parquet Record to a plain one.
   * <li>Remove the airbyte id and emission timestamp fields.</li>
   * <li>Remove null fields that must exist in Parquet but does not in original Json.</li> This
   * function mutates the input Json.
   */
  public static JsonNode pruneAirbyteJson(JsonNode input) {
    ObjectNode output = (ObjectNode) input;

    // Remove Airbyte columns.
    output.remove(JavaBaseConstants.COLUMN_NAME_AB_ID);
    output.remove(JavaBaseConstants.COLUMN_NAME_EMITTED_AT);

    // Fields with null values does not exist in the original Json but only in Parquet.
    for (String field : MoreIterators.toList(output.fieldNames())) {
      if (output.get(field) == null || output.get(field).isNull()) {
        output.remove(field);
      }
    }

    return output;
  }

}
