/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.destination.s3.util.S3NameTransformer;

public final class S3DestinationConstants {

  public static final String YYYY_MM_DD_FORMAT_STRING = "yyyy_MM_dd";
  public static final S3NameTransformer NAME_TRANSFORMER = new S3NameTransformer();
  public static final String PART_SIZE_MB_ARG_NAME = "part_size_mb";
  public static final int DEFAULT_PART_SIZE_MB = 10;
  public static final String DEFAULT_PATH_FORMAT = "${NAMESPACE}/${STREAM_NAME}/";

  private S3DestinationConstants() {}

}
