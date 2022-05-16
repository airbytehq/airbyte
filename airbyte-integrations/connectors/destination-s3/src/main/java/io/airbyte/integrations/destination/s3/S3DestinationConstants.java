/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.S3NameTransformer;

public final class S3DestinationConstants {

  public static final String YYYY_MM_DD_FORMAT_STRING = "yyyy_MM_dd";
  public static final S3NameTransformer NAME_TRANSFORMER = new S3NameTransformer();
  public static final String PART_SIZE_MB_ARG_NAME = "part_size_mb";
  // The smallest part size is 5MB. An S3 upload can be maximally formed of 10,000 parts. This gives
  // us an upper limit of 10,000 * 10 / 1000 = 100 GB per table with a 10MB part size limit.
  // WARNING: Too large a part size can cause potential OOM errors.
  public static final int DEFAULT_PART_SIZE_MB = 10;
  public static final String DEFAULT_PATH_FORMAT = "${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_";

  // gzip compression for CSV and JSONL
  public static final String COMPRESSION_ARG_NAME = "compression";
  public static final String COMPRESSION_TYPE_ARG_NAME = "compression_type";
  public static final CompressionType DEFAULT_COMPRESSION_TYPE = CompressionType.GZIP;

  private S3DestinationConstants() {}

}
