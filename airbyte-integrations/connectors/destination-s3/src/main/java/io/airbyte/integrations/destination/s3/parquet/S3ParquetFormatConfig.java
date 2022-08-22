/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

public class S3ParquetFormatConfig implements S3FormatConfig {

  public static final String PARQUET_SUFFIX = ".parquet";

  private final CompressionCodecName compressionCodec;
  private final int blockSize;
  private final int maxPaddingSize;
  private final int pageSize;
  private final int dictionaryPageSize;
  private final boolean dictionaryEncoding;

  public S3ParquetFormatConfig(final JsonNode formatConfig) {
    final int blockSizeMb = S3FormatConfig.withDefault(formatConfig, "block_size_mb", S3ParquetConstants.DEFAULT_BLOCK_SIZE_MB);
    final int maxPaddingSizeMb = S3FormatConfig.withDefault(formatConfig, "max_padding_size_mb", S3ParquetConstants.DEFAULT_MAX_PADDING_SIZE_MB);
    final int pageSizeKb = S3FormatConfig.withDefault(formatConfig, "page_size_kb", S3ParquetConstants.DEFAULT_PAGE_SIZE_KB);
    final int dictionaryPageSizeKb =
        S3FormatConfig.withDefault(formatConfig, "dictionary_page_size_kb", S3ParquetConstants.DEFAULT_DICTIONARY_PAGE_SIZE_KB);

    this.compressionCodec = CompressionCodecName
        .valueOf(S3FormatConfig.withDefault(formatConfig, "compression_codec", S3ParquetConstants.DEFAULT_COMPRESSION_CODEC.name()).toUpperCase());
    this.blockSize = blockSizeMb * 1024 * 1024;
    this.maxPaddingSize = maxPaddingSizeMb * 1024 * 1024;
    this.pageSize = pageSizeKb * 1024;
    this.dictionaryPageSize = dictionaryPageSizeKb * 1024;
    this.dictionaryEncoding = S3FormatConfig.withDefault(formatConfig, "dictionary_encoding", S3ParquetConstants.DEFAULT_DICTIONARY_ENCODING);
  }

  @Override
  public S3Format getFormat() {
    return S3Format.PARQUET;
  }

  @Override
  public String getFileExtension() {
    return PARQUET_SUFFIX;
  }

  public CompressionCodecName getCompressionCodec() {
    return compressionCodec;
  }

  public int getBlockSize() {
    return blockSize;
  }

  public int getMaxPaddingSize() {
    return maxPaddingSize;
  }

  public int getPageSize() {
    return pageSize;
  }

  public int getDictionaryPageSize() {
    return dictionaryPageSize;
  }

  public boolean isDictionaryEncoding() {
    return dictionaryEncoding;
  }

  @Override
  public String toString() {
    return "S3ParquetFormatConfig{" +
        "compressionCodec=" + compressionCodec + ", " +
        "blockSize=" + blockSize + ", " +
        "maxPaddingSize=" + maxPaddingSize + ", " +
        "pageSize=" + pageSize + ", " +
        "dictionaryPageSize=" + dictionaryPageSize + ", " +
        "dictionaryEncoding=" + dictionaryEncoding + ", " +
        '}';
  }

}
