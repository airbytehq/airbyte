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

package io.airbyte.integrations.debezium;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.Test;

class AirbyteFileOffsetBackingStoreTest {

  @SuppressWarnings("UnstableApiUsage")
  @Test
  void test() throws IOException {
    final Path testRoot = Files.createTempDirectory(Path.of("/tmp"), "offset-store-test");

    final byte[] bytes = MoreResources.readBytes("test_debezium_offset.dat");
    final Path templateFilePath = testRoot.resolve("template_offset.dat");
    IOs.writeFile(templateFilePath, bytes);

    final Path writeFilePath = testRoot.resolve("offset.dat");

    final AirbyteFileOffsetBackingStore offsetStore = new AirbyteFileOffsetBackingStore(templateFilePath);
    Map<String, String> offset = offsetStore.read();

    final JsonNode asJson = Jsons.jsonNode(offset);

    final AirbyteFileOffsetBackingStore offsetStore2 = new AirbyteFileOffsetBackingStore(writeFilePath);
    offsetStore2.persist(asJson);

    final Map<String, String> stateFromOffsetStoreRoundTrip = offsetStore2.read();

    // verify that, after a round trip through the offset store, we get back the same data.
    assertEquals(offset, stateFromOffsetStoreRoundTrip);
    // verify that the file written by the offset store is identical to the template file.
    assertTrue(com.google.common.io.Files.equal(templateFilePath.toFile(), writeFilePath.toFile()));
  }

}
