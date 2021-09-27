/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
