package io.airbyte.integrations.destination.s3.parquet;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.junit.jupiter.api.Test;

class S3ParquetFormatConfigTest {

  @Test
  public void testParameterByteConversion() {
    // The constructor should automatically convert MB or KB to bytes.
    S3ParquetFormatConfig config = new S3ParquetFormatConfig(
        CompressionCodecName.BROTLI,
        1,
        1,
        1,
        1,
        true
    );
    assertEquals(1024 * 1024, config.getBlockSize());
    assertEquals(1024 * 1024, config.getMaxPaddingSize());
    assertEquals(1024, config.getPageSize());
    assertEquals(1024, config.getDictionaryPageSize());
  }

}
