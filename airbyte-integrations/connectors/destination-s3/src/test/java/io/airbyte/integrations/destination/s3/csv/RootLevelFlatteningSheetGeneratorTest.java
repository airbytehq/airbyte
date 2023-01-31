/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

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
    final List<String> fields = Lists.newArrayList("C", "B", "A", "c", "b", "a");
    Collections.shuffle(fields);

    final ObjectNode schemaProperties = MAPPER.createObjectNode();
    for (final String field : fields) {
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
    final ObjectNode json = MAPPER.createObjectNode();
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
