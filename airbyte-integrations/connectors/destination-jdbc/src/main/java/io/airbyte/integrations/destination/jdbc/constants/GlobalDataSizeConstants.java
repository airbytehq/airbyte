package io.airbyte.integrations.destination.jdbc.constants;

import io.aesy.datasize.ByteUnit.IEC;
import io.aesy.datasize.DataSize;

public interface GlobalDataSizeConstants {
  /** 256 MB to BYTES as comparison will be done in BYTES */
  int DEFAULT_MAX_BATCH_SIZE_BYTES = DataSize.of(256L, IEC.MEBIBYTE).toUnit(IEC.BYTE).getValue().intValue();
  /** This constant determines the max possible size of file(e.g. 1 GB / 256 megabytes ≈ 4 chunks of file)
  see StagingFilenameGenerator.java:28
  */
  long MAX_FILE_SIZE = DataSize.of(1L, IEC.GIBIBYTE).toUnit(IEC.BYTE).getValue().longValue();
}
