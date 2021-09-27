/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class JsonSchemas {

  /**
   * JsonSchema supports to ways of declaring type. `type: "string"` and `type: ["null", "string"]`.
   * This method will mutate a JsonNode with a type field so that the output type is the array
   * version.
   *
   * @param jsonNode - a json object with children that contain types.
   */
  public static void mutateTypeToArrayStandard(final JsonNode jsonNode) {
    if (jsonNode.get("type") != null && !jsonNode.get("type").isArray()) {
      final JsonNode type = jsonNode.get("type");
      ((ObjectNode) jsonNode).putArray("type").add(type);
    }
  }

  /*
   * JsonReferenceProcessor relies on all of the json in consumes being in a file system (not in a
   * jar). This method copies all of the json configs out of the jar into a temporary directory so
   * that JsonReferenceProcessor can find them.
   */
  public static <T> Path prepareSchemas(final String resourceDir, Class<T> klass) {
    try {
      List<String> filenames;
      try (Stream<Path> resources = MoreResources.listResources(klass, resourceDir)) {
        filenames = resources.map(p -> p.getFileName().toString())
            .filter(p -> p.endsWith(".yaml"))
            .collect(Collectors.toList());
      }

      final Path configRoot = Files.createTempDirectory("schemas");
      for (String filename : filenames) {
        IOs.writeFile(
            configRoot,
            filename,
            MoreResources.readResource(String.format("%s/%s", resourceDir, filename)));
      }

      return configRoot;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

}
