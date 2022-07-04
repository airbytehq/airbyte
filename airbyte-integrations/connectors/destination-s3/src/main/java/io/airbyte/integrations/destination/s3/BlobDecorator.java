/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.google.common.annotations.VisibleForTesting;
import java.io.OutputStream;
import java.util.Map;

/**
 * Represents the ability to modify how a blob is stored, by modifying the data being written and/or
 * the blob's metadata.
 */
public interface BlobDecorator {

  OutputStream wrap(OutputStream stream);

  /**
   * Modifies the blob's metadata.
   * <p>
   * In the most common case, BlobDecorator implementations will insert new entries into the metadata
   * map. These entries may be vendor-specific. The metadataKeyMapping parameter defines a mapping
   * from the "canonical" keys to the vendor-specific keys. See
   * {@link S3StorageOperations#getMetadataMapping()} for an example.
   * <p>
   * If a key is not defined in metadataKeyMapping, it will not be inserted into the metadata.
   *
   * @param metadata The blob's metadata
   * @param metadataKeyMapping The mapping from canonical to vendor-specific key names
   */
  void updateMetadata(Map<String, String> metadata, Map<String, String> metadataKeyMapping);

  /**
   * A convenience method for subclasses. Handles inserting new metadata entries according to the
   * metadataKeyMapping.
   */
  @VisibleForTesting
  static void insertMetadata(final Map<String, String> metadata,
                             final Map<String, String> metadataKeyMapping,
                             final String key,
                             final String value) {
    if (metadataKeyMapping.containsKey(key)) {
      metadata.put(metadataKeyMapping.get(key), value);
    }
  }

}
