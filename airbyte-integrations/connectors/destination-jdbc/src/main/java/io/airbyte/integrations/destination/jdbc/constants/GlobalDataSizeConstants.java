package io.airbyte.integrations.destination.jdbc.constants;

import io.aesy.datasize.ByteUnit.IEC;
import io.aesy.datasize.DataSize;

public interface GlobalDataSizeConstants {
  /** 256 MB to BYTES as comparison will be done in BYTES */
  int DEFAULT_MAX_BATCH_SIZE_BYTES = DataSize.of(256L, IEC.MEBIBYTE).toUnit(IEC.BYTE).getValue().intValue();
  /** This constant determines the max size of uploaded chunk of file(e.g. 15 GB / 256 megabytes ≈ 58 MB per chunk of file)
  see StagingFilenameGenerator.java:28
  */
  long MAX_BYTE_PARTS_PER_FILE_DEFAULT = DataSize.of(15L, IEC.GIBIBYTE).toUnit(IEC.BYTE).getValue().longValue();

  long MAX_BYTE_PARTS_PER_FILE_SNOWFLAKE = DataSize.of(700L, IEC.MEBIBYTE).toUnit(IEC.BYTE).getValue().longValue();
}
