package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class BlobDecoratorTest {

  private static class TestBlobDecorator implements BlobDecorator {
    @Override
    public OutputStream wrap(final OutputStream stream) {
      return null;
    }
    @Override
    public void updateMetadata(final Map<String, String> metadata, final Map<String, String> metadataKeyMapping) {
    }
  }

  @Test
  public void testOverwriteMetadata() {
    final BlobDecorator decorator = new TestBlobDecorator();
    final Map<String, String> metadata = new HashMap<>();
    metadata.put("amz-foo", "oldValue");

    decorator.insertMetadata(
        metadata,
        Map.of("foo", "amz-foo"),
        "foo", "newValue"
    );

    assertEquals(Map.of("amz-foo", "newValue"), metadata);
  }

  @Test
  public void testNewMetadata() {
    final BlobDecorator decorator = new TestBlobDecorator();
    final Map<String, String> metadata = new HashMap<>();
    metadata.put("amz-foo", "oldValue");

    decorator.insertMetadata(
        metadata,
        Map.of("bar", "amz-bar"),
        "bar", "newValue"
    );

    assertEquals(
        Map.of(
            "amz-foo", "oldValue",
            "amz-bar", "newValue"
        ),
        metadata
    );
  }

  @Test
  public void testSkipMetadata() {
    final BlobDecorator decorator = new TestBlobDecorator();
    final Map<String, String> metadata = new HashMap<>();
    metadata.put("amz-foo", "oldValue");

    decorator.insertMetadata(
        metadata,
        Map.of("foo", "amz-foo"),
        "bar", "newValue"
    );

    assertEquals(Map.of("amz-foo", "oldValue"), metadata);
  }
}
