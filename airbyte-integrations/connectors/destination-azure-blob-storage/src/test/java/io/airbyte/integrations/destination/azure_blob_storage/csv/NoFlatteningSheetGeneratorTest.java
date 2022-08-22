/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
    final ObjectNode json = mapper.createObjectNode();
    json.set("Field 4", mapper.createObjectNode().put("Field 41", 15));
    json.put("Field 1", "A");
    json.put("Field 3", 71);
    json.put("Field 2", true);

    assertLinesMatch(
        Collections.singletonList("{\"Field 4\":{\"Field 41\":15},\"Field 1\":\"A\",\"Field 3\":71,\"Field 2\":true}"),
        sheetGenerator.getRecordColumns(json));
  }

}
