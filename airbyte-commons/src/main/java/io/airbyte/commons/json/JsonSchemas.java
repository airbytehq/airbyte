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
