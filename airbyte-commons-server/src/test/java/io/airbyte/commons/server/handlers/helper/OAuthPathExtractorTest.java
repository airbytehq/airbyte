/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers.helper;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.handlers.helpers.OAuthPathExtractor;
import java.util.List;
import java.util.Map;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

class OAuthPathExtractorTest {

  @Test
  void testExtract() {
    final JsonNode input = Jsons.deserialize("""
                                             {
                                                     "type": "object",
                                                     "additionalProperties": false,
                                                     "properties": {
                                                       "tenant_id": {
                                                         "type": "string",
                                                         "path_in_connector_config": ["tenant_id"]
                                                       },
                                                       "another_property": {
                                                         "type": "string",
                                                         "path_in_connector_config": ["another", "property"]
                                                       }
                                                     }
                                                   }
                                             """);

    final Map<String, List<String>> expected = Map.ofEntries(
        Map.entry("tenant_id", List.of("tenant_id")),
        Map.entry("another_property", List.of("another", "property")));

    Assertions.assertThat(OAuthPathExtractor.extractOauthConfigurationPaths(input))
        .containsExactlyInAnyOrderEntriesOf(expected);
  }

}
