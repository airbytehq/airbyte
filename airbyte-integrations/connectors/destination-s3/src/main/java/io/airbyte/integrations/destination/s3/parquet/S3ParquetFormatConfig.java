/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

public record S3ParquetFormatConfig(
    CompressionCodecName compressionCodec,
    int blockSize,
    int maxPaddingSize,
    int pageSize,
    int dictionaryPageSize,
    boolean dictionaryEncoding
) implements S3FormatConfig {

  public S3ParquetFormatConfig(final JsonNode formatConfig) {
    this(
        CompressionCodecName.valueOf(
            S3FormatConfig.withDefault(formatConfig, "compression_codec", S3ParquetConstants.DEFAULT_COMPRESSION_CODEC.name()).toUpperCase()),
        S3FormatConfig.withDefault(formatConfig, "block_size_mb", S3ParquetConstants.DEFAULT_BLOCK_SIZE_MB) * 1024 * 1024,
        S3FormatConfig.withDefault(formatConfig, "max_padding_size_mb", S3ParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB) * 1024 * 1024,
        S3FormatConfig.withDefault(formatConfig, "page_size_kb", S3ParquetConstants.DEFAULT_PAGE_SIZE_KB) * 1024,
        S3FormatConfig.withDefault(formatConfig, "dictionary_page_size_kb", S3ParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB) * 1024,
        S3FormatConfig.withDefault(formatConfig, "dictionary_encoding", S3ParquetConstants.DEFAULT_DICTIONARY_ENCODING)
    );
  }

  @Override
  public S3Format format() {
    return S3Format.PARQUET;
  }

  @Override
  public Long partSize() {
    // not applicable for Parquet format
    return null;
  }
}
