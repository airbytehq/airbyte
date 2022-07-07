/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.COMPRESSION_TYPE_ARG_NAME;
import static io.airbyte.integrations.destination.s3.S3DestinationConstants.DEFAULT_COMPRESSION_TYPE;

import com.fasterxml.jackson.databind.JsonNode;

public class CompressionTypeHelper {

  private CompressionTypeHelper() {}

  /**
   * Sample expected input: { "compression_type": "No Compression" }
   */
  public static CompressionType parseCompressionType(final JsonNode compressionConfig) {
    if (compressionConfig == null || compressionConfig.isNull()) {
      return DEFAULT_COMPRESSION_TYPE;
    }
    final String compressionType = compressionConfig.get(COMPRESSION_TYPE_ARG_NAME).asText();
    if (compressionType.toUpperCase().equals(CompressionType.GZIP.name())) {
      return CompressionType.GZIP;
    } else {
      return CompressionType.NO_COMPRESSION;
    }
  }

}
