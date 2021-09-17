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

  public RootLevelFlatteningSheetGenerator(JsonNode jsonSchema) {
    this.recordHeaders = MoreIterators.toList(jsonSchema.get("properties").fieldNames())
        .stream().sorted().collect(Collectors.toList());;
  }

  @Override
  public List<String> getHeaderRow() {
    List<String> headers = Lists.newArrayList(JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    headers.addAll(recordHeaders);
    return headers;
  }

  /**
   * With root level flattening, the record columns are the first level fields of the json.
   */
  @Override
  List<String> getRecordColumns(JsonNode json) {
    List<String> values = new LinkedList<>();
    for (String field : recordHeaders) {
      JsonNode value = json.get(field);
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
