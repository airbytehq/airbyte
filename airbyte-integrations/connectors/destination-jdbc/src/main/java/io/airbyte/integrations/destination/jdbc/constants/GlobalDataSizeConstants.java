/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.constants;

import io.aesy.datasize.ByteUnit.IEC;
import io.aesy.datasize.DataSize;

public interface GlobalDataSizeConstants {

  /** 25 MB to BYTES as comparison will be done in BYTES */
  int DEFAULT_MAX_BATCH_SIZE_BYTES = DataSize.of(25L, IEC.MEBIBYTE).toUnit(IEC.BYTE).getValue().intValue();
  /**
   * This constant determines the max possible size of file(e.g. 100 MB / 25 megabytes ≈ 4 chunks of
   * file) see StagingFilenameGenerator.java:28
   */
  long MAX_FILE_SIZE = DataSize.of(100L, IEC.MEBIBYTE).toUnit(IEC.BYTE).getValue().longValue();

}
