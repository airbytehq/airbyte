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

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class MigrationTestUtils {

  public static Map<ResourceId, Stream<JsonNode>> convertListsToValues(Map<ResourceId, List<JsonNode>> map) {
    return map.entrySet()
        .stream()
        .collect(Collectors.toMap(Entry::getKey, entry -> entry.getValue().stream().map(Jsons::clone)));
  }

  public static Map<ResourceId, ListConsumer<JsonNode>> createOutputConsumer(Set<ResourceId> resourceIds) {
    return resourceIds.stream().collect(Collectors.toMap(v -> v, v -> new ListConsumer<>()));
  }

  public static Map<ResourceId, List<JsonNode>> createExpectedOutput(Set<ResourceId> resourceIds, Map<ResourceId, List<JsonNode>> overrides) {
    return resourceIds.stream().collect(Collectors.toMap(v -> v, v -> {
      if (overrides.containsKey(v)) {
        return overrides.get(v);
      } else {
        return new ArrayList<>();
      }
    }));
  }

  public static Map<ResourceId, List<JsonNode>> collectConsumersToList(Map<ResourceId, ListConsumer<JsonNode>> input) {
    return input.entrySet()
        .stream()
        .collect(Collectors.toMap(
            Entry::getKey,
            e -> e.getValue().getConsumed()));
  }

}
