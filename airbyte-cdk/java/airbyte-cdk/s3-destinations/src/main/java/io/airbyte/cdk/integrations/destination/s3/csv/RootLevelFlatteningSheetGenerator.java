/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.csv;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.protocol.deser.PartialJsonDeserializer;
import io.airbyte.cdk.protocol.deser.StringIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class RootLevelFlatteningSheetGenerator extends BaseSheetGenerator implements CsvSheetGenerator {

  /**
   * Keep a header list to iterate the input json object with a defined order.
   */
  private final List<String> recordHeaders;

  public RootLevelFlatteningSheetGenerator(final JsonNode jsonSchema) {
    this.recordHeaders = MoreIterators.toList(jsonSchema.get("properties").fieldNames())
        .stream().sorted().collect(Collectors.toList());
  }

  @Override
  public List<String> getHeaderRow() {
    final List<String> headers = Lists.newArrayList(JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    headers.addAll(recordHeaders);
    return headers;
  }

  /**
   * With root level flattening, the record columns are the first level fields of the json.
   */
  @Override
  List<String> getRecordColumns(final String serializedJson) {
    final Map<String, String> fields = PartialJsonDeserializer.parseObject(new StringIterator(serializedJson), recordHeaders);

    final List<String> output = new ArrayList<>();
    for (final String field : recordHeaders) {
      final String serializedValue = fields.getOrDefault(field, "");
      if (serializedValue.startsWith("\"")) {
        // Unwrap string values, i.e. we want to remove the double quotes,
        // handle escape characters, etc.
        // TODO it would be cool to do this within the deserializer, i.e. 1-pass processing
        output.add(Jsons.deserialize(serializedValue).asText());
      } else if ("null".equals(serializedValue)) {
        // Write empty string instead of null
        output.add("");
      } else {
        // For other values (numbers, booleans, arrays, objects) just write the raw serialized value
        output.add(serializedValue);
      }
    }
    return output;
  }

}
