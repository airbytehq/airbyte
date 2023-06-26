/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
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
    final Path secondWriteFilePath = testRoot.resolve("offset_2.dat");

    final AirbyteFileOffsetBackingStore offsetStore = new AirbyteFileOffsetBackingStore(templateFilePath, Optional.empty());
    final Map<String, String> offset = offsetStore.read();

    final AirbyteFileOffsetBackingStore offsetStore2 = new AirbyteFileOffsetBackingStore(writeFilePath, Optional.empty());
    offsetStore2.persist(Jsons.jsonNode(offset));
    final Map<String, String> stateFromOffsetStore2 = offsetStore2.read();

    final AirbyteFileOffsetBackingStore offsetStore3 = new AirbyteFileOffsetBackingStore(secondWriteFilePath, Optional.empty());
    offsetStore3.persist(Jsons.jsonNode(stateFromOffsetStore2));
    final Map<String, String> stateFromOffsetStore3 = offsetStore3.read();

    // verify that, after a round trip through the offset store, we get back the same data.
    assertEquals(stateFromOffsetStore2, stateFromOffsetStore3);
    // verify that the file written by the offset store is identical to the template file.
    assertTrue(com.google.common.io.Files.equal(secondWriteFilePath.toFile(), writeFilePath.toFile()));
  }

  @Test
  void test2() throws IOException {
    final Path testRoot = Files.createTempDirectory(Path.of("/tmp"), "offset-store-test");

    final byte[] bytes = MoreResources.readBytes("test_debezium_offset.dat");
    final Path templateFilePath = testRoot.resolve("template_offset.dat");
    IOs.writeFile(templateFilePath, bytes);

    final Path writeFilePath = testRoot.resolve("offset.dat");
    final Path secondWriteFilePath = testRoot.resolve("offset_2.dat");

    final AirbyteFileOffsetBackingStore offsetStore = new AirbyteFileOffsetBackingStore(templateFilePath, Optional.of("orders"));
    final Map<String, String> offset = offsetStore.read();

    final AirbyteFileOffsetBackingStore offsetStore2 = new AirbyteFileOffsetBackingStore(writeFilePath, Optional.of("orders"));
    offsetStore2.persist(Jsons.jsonNode(offset));
    final Map<String, String> stateFromOffsetStore2 = offsetStore2.read();

    final AirbyteFileOffsetBackingStore offsetStore3 = new AirbyteFileOffsetBackingStore(secondWriteFilePath, Optional.of("orders"));
    offsetStore3.persist(Jsons.jsonNode(stateFromOffsetStore2));
    final Map<String, String> stateFromOffsetStore3 = offsetStore3.read();

    // verify that, after a round trip through the offset store, we get back the same data.
    assertEquals(stateFromOffsetStore2, stateFromOffsetStore3);
    // verify that the file written by the offset store is identical to the template file.
    assertTrue(com.google.common.io.Files.equal(secondWriteFilePath.toFile(), writeFilePath.toFile()));
  }

}
