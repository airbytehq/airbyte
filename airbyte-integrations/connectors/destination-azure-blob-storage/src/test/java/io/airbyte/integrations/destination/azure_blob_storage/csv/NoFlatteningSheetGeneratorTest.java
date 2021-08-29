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
import org.junit.jupiter.api.Test;

class NoFlatteningSheetGeneratorTest {

  private final ObjectMapper mapper = MoreMappers.initMapper();
  private final NoFlatteningSheetGenerator sheetGenerator = new NoFlatteningSheetGenerator();

  @Test
  public void testGetHeaderRow() {
    assertLinesMatch(
        Lists.newArrayList(
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA),
        sheetGenerator.getHeaderRow());
  }

  @Test
  public void testGetRecordColumns() {
    ObjectNode json = mapper.createObjectNode();
    json.set("Field 4", mapper.createObjectNode().put("Field 41", 15));
    json.put("Field 1", "A");
    json.put("Field 3", 71);
    json.put("Field 2", true);

    assertLinesMatch(
        Collections.singletonList("{\"Field 4\":{\"Field 41\":15},\"Field 1\":\"A\",\"Field 3\":71,\"Field 2\":true}"),
        sheetGenerator.getRecordColumns(json));
  }

}
