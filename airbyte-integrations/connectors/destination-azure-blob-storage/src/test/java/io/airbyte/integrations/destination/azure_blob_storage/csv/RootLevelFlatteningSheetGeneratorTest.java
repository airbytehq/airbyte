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

import static org.junit.jupiter.api.Assertions.assertLinesMatch;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RootLevelFlatteningSheetGeneratorTest {

  private final static ObjectMapper MAPPER = MoreMappers.initMapper();
  private final static ObjectNode SCHEMA = MAPPER.createObjectNode();
  static {
    List<String> fields = Lists.newArrayList("C", "B", "A", "c", "b", "a");
    Collections.shuffle(fields);

    ObjectNode schemaProperties = MAPPER.createObjectNode();
    for (String field : fields) {
      schemaProperties.set(field, MAPPER.createObjectNode());
    }

    SCHEMA.set("properties", schemaProperties);
  }

  private RootLevelFlatteningSheetGenerator sheetGenerator;

  @BeforeEach
  public void createGenerator() {
    this.sheetGenerator = new RootLevelFlatteningSheetGenerator(SCHEMA);
  }

  @Test
  public void testGetHeaderRow() {
    assertLinesMatch(
        Lists.newArrayList(
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            "A", "B", "C", "a", "b", "c"),
        sheetGenerator.getHeaderRow());
  }

  @Test
  public void testGetRecordColumns() {
    ObjectNode json = MAPPER.createObjectNode();
    // Field c is missing
    json.put("C", 3);
    json.put("B", "value B");
    json.set("A", MAPPER.createObjectNode().put("Field 41", 15));
    json.put("b", "value b");
    json.put("a", 1);

    assertLinesMatch(
        // A, B, C, a, b, c
        Lists.newArrayList("{\"Field 41\":15}", "value B", "3", "1", "value b", ""),
        sheetGenerator.getRecordColumns(json));
  }

}
