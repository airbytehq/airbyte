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

package io.airbyte.integrations.destination;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.text.Names;
import io.airbyte.commons.util.MoreIterators;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

public class StandardNameTransformer implements NamingConventionTransformer {

  private static final String NON_JSON_PATH_CHARACTERS_PATTERN = "['\"`]";

  @Override
  public String getIdentifier(String name) {
    return convertStreamName(name);
  }

  @Override
  public String getRawTableName(String streamName) {
    return convertStreamName("_airbyte_raw_" + streamName);
  }

  @Override
  public String getTmpTableName(String streamName) {
    return convertStreamName(Strings.addRandomSuffix("_airbyte_tmp", "_", 3) + "_" + streamName);
  }

  protected String convertStreamName(String input) {
    return Names.toAlphanumericAndUnderscore(input);
  }

  /**
   * Rebuild a JsonNode adding sanitized property names (a subset of special characters replaced by
   * underscores) while keeping original property names too. This is needed by some destinations as
   * their json extract functions have limitations on how such special characters are parsed. These
   * naming rules may be different to schema/table/column naming conventions.
   */
  public static JsonNode formatJsonPath(JsonNode root) {
    if (root.isObject()) {
      final Map<String, JsonNode> properties = new HashMap<>();
      var keys = Jsons.keys(root);
      for (var key : keys) {
        final JsonNode property = root.get(key);
        // keep original key
        properties.put(key, formatJsonPath(property));
      }
      for (var key : keys) {
        final JsonNode property = root.get(key);
        final String formattedKey = key.replaceAll(NON_JSON_PATH_CHARACTERS_PATTERN, "_");
        if (!properties.containsKey(formattedKey)) {
          // duplicate property in a formatted key to be extracted in normalization
          properties.put(formattedKey, formatJsonPath(property));
        }
      }
      return Jsons.jsonNode(properties);
    } else if (root.isArray()) {
      return Jsons.jsonNode(MoreIterators.toList(root.elements()).stream()
          .map(StandardNameTransformer::formatJsonPath)
          .collect(Collectors.toList()));
    } else {
      return root;
    }
  }

}
