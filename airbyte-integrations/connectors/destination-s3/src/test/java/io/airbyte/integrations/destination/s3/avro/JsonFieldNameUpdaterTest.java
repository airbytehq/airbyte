/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import java.io.IOException;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class JsonFieldNameUpdaterTest {

  @Test
  public void testFieldNameUpdate() throws IOException {
    JsonNode testCases = Jsons.deserialize(MoreResources.readResource("parquet/json_field_name_updater/test_case.json"));
    for (JsonNode testCase : testCases) {
      JsonNode nameMap = testCase.get("nameMap");
      JsonFieldNameUpdater nameUpdater = new JsonFieldNameUpdater(
          MoreIterators.toList(nameMap.fields()).stream()
              .collect(Collectors.toMap(Entry::getKey, e -> e.getValue().asText())));

      JsonNode original = testCase.get("original");
      JsonNode updated = testCase.get("updated");

      assertEquals(updated, nameUpdater.getJsonWithStandardizedFieldNames(original));
      assertEquals(original, nameUpdater.getJsonWithOriginalFieldNames(updated));
    }
  }

}
