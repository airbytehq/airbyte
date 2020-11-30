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

package io.airbyte.config.init;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.yaml.Yamls;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RepositorySeedTest {

  private static final String CONFIG_ID = "configId";
  private static final JsonNode OBJECT = Jsons.jsonNode(ImmutableMap.builder()
      .put(CONFIG_ID, UUID.randomUUID())
      .put("name", "barker")
      .put("description", "playwright")
      .build());

  private Path input;
  private Path output;

  @BeforeEach
  void setup() throws IOException {
    input = Files.createTempDirectory("test_input").resolve("input.yaml");
    output = Files.createTempDirectory("test_output");

    writeSeedList(OBJECT);
  }

  @Test
  void testWrite() throws IOException {
    new RepositorySeed().run(CONFIG_ID, input, output);
    final JsonNode actual = Jsons.deserialize(IOs.readFile(output, OBJECT.get(CONFIG_ID).asText() + ".json"));
    assertEquals(OBJECT, actual);
  }

  @Test
  void testOverwrites() throws IOException {
    new RepositorySeed().run(CONFIG_ID, input, output);
    final JsonNode actual = Jsons.deserialize(IOs.readFile(output, OBJECT.get(CONFIG_ID).asText() + ".json"));
    assertEquals(OBJECT, actual);

    final JsonNode clone = Jsons.clone(OBJECT);
    ((ObjectNode) clone).put("description", "revolutionary");
    writeSeedList(clone);

    new RepositorySeed().run(CONFIG_ID, input, output);
    final JsonNode actualAfterOverwrite = Jsons.deserialize(IOs.readFile(output, OBJECT.get(CONFIG_ID).asText() + ".json"));
    assertEquals(clone, actualAfterOverwrite);
  }

  @Test
  void testPristineOutputDir() throws IOException {
    IOs.writeFile(output, "blah.json", "{}");
    assertEquals(1, Files.list(output).count());

    new RepositorySeed().run(CONFIG_ID, input, output);

    // verify the file that the file that was already in the directory is gone.
    assertEquals(1, Files.list(output).count());
    assertEquals(OBJECT.get(CONFIG_ID).asText() + ".json", Files.list(output).collect(Collectors.toList()).get(0).getFileName().toString());
  }

  private void writeSeedList(JsonNode seed) {
    final JsonNode seedList = Jsons.jsonNode(new ArrayList<>());
    ((ArrayNode) seedList).add(seed);
    IOs.writeFile(input, Yamls.serialize(seedList));
  }

}
