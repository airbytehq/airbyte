/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.S3NameTransformer;

public final class S3DestinationConstants {

  public static final String YYYY_MM_DD_FORMAT_STRING = "yyyy_MM_dd";
  public static final S3NameTransformer NAME_TRANSFORMER = new S3NameTransformer();
  public static final String DEFAULT_PATH_FORMAT = "${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_";

  // gzip compression for CSV and JSONL
  public static final String COMPRESSION_ARG_NAME = "compression";
  public static final String COMPRESSION_TYPE_ARG_NAME = "compression_type";
  public static final String FLATTEN_DATA = "flatten_data";
  public static final CompressionType DEFAULT_COMPRESSION_TYPE = CompressionType.GZIP;

  private S3DestinationConstants() {}

}
