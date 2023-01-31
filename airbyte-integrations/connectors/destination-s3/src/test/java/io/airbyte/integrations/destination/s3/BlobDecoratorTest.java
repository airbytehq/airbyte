/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class BlobDecoratorTest {

  @Test
  public void testOverwriteMetadata() {
    final Map<String, String> metadata = new HashMap<>();
    metadata.put("amz-foo", "oldValue");

    BlobDecorator.insertMetadata(
        metadata,
        Map.of("foo", "amz-foo"),
        "foo", "newValue");

    assertEquals(Map.of("amz-foo", "newValue"), metadata);
  }

  @Test
  public void testNewMetadata() {
    final Map<String, String> metadata = new HashMap<>();
    metadata.put("amz-foo", "oldValue");

    BlobDecorator.insertMetadata(
        metadata,
        Map.of("bar", "amz-bar"),
        "bar", "newValue");

    assertEquals(
        Map.of(
            "amz-foo", "oldValue",
            "amz-bar", "newValue"),
        metadata);
  }

  @Test
  public void testSkipMetadata() {
    final Map<String, String> metadata = new HashMap<>();
    metadata.put("amz-foo", "oldValue");

    BlobDecorator.insertMetadata(
        metadata,
        Map.of("foo", "amz-foo"),
        "bar", "newValue");

    assertEquals(Map.of("amz-foo", "oldValue"), metadata);
  }

}
