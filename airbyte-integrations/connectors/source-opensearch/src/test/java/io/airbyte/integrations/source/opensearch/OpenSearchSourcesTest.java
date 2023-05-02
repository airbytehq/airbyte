/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.opensearch;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.opensearch.typemapper.OpenSearchTypeMapper;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class OpenSearchSourcesTest {

  @Test
  @DisplayName("Spec should match")
  public void specShouldMatch() throws Exception {
    final ConnectorSpecification actual = new OpenSearchSource().spec();
    final ConnectorSpecification expected = Jsons.deserialize(
        MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class);
    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("Actual mapper keyset should contain expected keyset")
  public void actualMapperKeySetShouldContainExpectedKeySet() {
    final Set<String> expectedKeySet = new HashSet<>(Arrays.asList(
        "binary", "boolean", "keyword",
        "long", "unsigned_long",
        "integer", "short", "byte", "double", "float",
        "half_float", "scaled_float", "date", "date_nanos", "ip",
        "text", "geo_point", "geo_shape"));
    Set<String> actualKeySet = new HashSet<>(OpenSearchTypeMapper.getMapper().keySet());

    assertTrue(actualKeySet.containsAll(expectedKeySet));
  }

  @Test
  @DisplayName("Formatter should transform objects conforming to airbyte spec")
  public void testFormatter() throws IOException, UnsupportedDatatypeException {
    final JsonNode input = Jsons.deserialize(
        MoreResources.readResource("sample_input.json"), JsonNode.class);
    final JsonNode expectedOutput = Jsons.deserialize(
        MoreResources.readResource("expected_output.json"), JsonNode.class);
    JsonNode actualOutput = OpenSearchTypeMapper.formatJSONSchema(input);
    assertEquals(expectedOutput, actualOutput);
  }

  @Test
  @DisplayName("Formatter should remove extra fields")
  public void testFormatterRemovals() throws IOException, UnsupportedDatatypeException {
    final JsonNode input = Jsons.deserialize(
        MoreResources.readResource("sample_input_extra_fields.json"), JsonNode.class);
    final JsonNode expectedOutput = Jsons.deserialize(
        MoreResources.readResource("expected_output_extra_fields.json"), JsonNode.class);
    JsonNode actualOutput = OpenSearchTypeMapper.formatJSONSchema(input);
    assertEquals(expectedOutput, actualOutput);
  }

}
