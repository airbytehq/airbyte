/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
    final Map<String, String> offset = offsetStore.read();

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
