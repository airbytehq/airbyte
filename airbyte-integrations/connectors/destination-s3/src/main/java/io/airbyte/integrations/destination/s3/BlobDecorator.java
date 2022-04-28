package io.airbyte.integrations.destination.s3;

import java.io.OutputStream;
import java.util.Map;

public interface BlobDecorator {
  OutputStream wrap(OutputStream stream);
  void updateMetadata(Map<String, String> metadata);
}
