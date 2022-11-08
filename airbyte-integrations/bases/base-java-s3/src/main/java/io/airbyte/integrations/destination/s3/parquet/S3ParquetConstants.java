/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import org.apache.parquet.hadoop.metadata.CompressionCodecName;

public class S3ParquetConstants {

  // Parquet writer
  public static final CompressionCodecName DEFAULT_COMPRESSION_CODEC = CompressionCodecName.UNCOMPRESSED;
  public static final int DEFAULT_BLOCK_SIZE_MB = 128;
  public static final int DEFAULT_MAX_PADDING_SIZE_MB = 8;
  public static final int DEFAULT_PAGE_SIZE_KB = 1024;
  public static final int DEFAULT_DICTIONARY_PAGE_SIZE_KB = 1024;
  public static final boolean DEFAULT_DICTIONARY_ENCODING = true;

}
