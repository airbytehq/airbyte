/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.csv;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;

public class RootLevelFlatteningSheetGenerator extends BaseSheetGenerator implements CsvSheetGenerator {

  /**
   * Keep a header list to iterate the input json object with a defined order.
   */
  private final List<String> recordHeaders;

  public RootLevelFlatteningSheetGenerator(final JsonNode jsonSchema) {
    this.recordHeaders = MoreIterators.toList(jsonSchema.get("properties").fieldNames())
        .stream().sorted().collect(Collectors.toList());;
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
  List<String> getRecordColumns(final JsonNode json) {
    final List<String> values = new LinkedList<>();
    for (final String field : recordHeaders) {
      final JsonNode value = json.get(field);
      if (value == null) {
        values.add("");
      } else if (value.isValueNode()) {
        // Call asText method on value nodes so that proper string
        // representation of json values can be returned by Jackson.
        // Otherwise, CSV printer will just call the toString method,
        // which can be problematic (e.g. text node will have extra
        // double quotation marks around its text value).
        values.add(value.asText());
      } else {
        values.add(Jsons.serialize(value));
      }
    }

    return values;
  }

}
