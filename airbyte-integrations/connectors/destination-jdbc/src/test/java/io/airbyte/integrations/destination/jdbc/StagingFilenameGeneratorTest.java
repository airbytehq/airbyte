/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import static org.junit.jupiter.api.Assertions.*;

import io.aesy.datasize.ByteUnit.IEC;
import io.aesy.datasize.DataSize;
import io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

class StagingFilenameGeneratorTest {

  private static final String STREAM_NAME = RandomStringUtils.randomAlphabetic(5).toLowerCase();
  // Equal to GlobalDataSizeConstants.MAX_BYTE_PARTS_PER_FILE / GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES
  // because <insert explanation here>
  private static final int EXPECTED_ITERATIONS_WITH_STANDARD_BYTE_BUFFER = 4;
  private static final StagingFilenameGenerator FILENAME_GENERATOR =
      new StagingFilenameGenerator(STREAM_NAME, GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES);

  @Test
  public void testGetStagingFilename() {
    // the file suffix increments after every MAX_PARTS_PER_FILE method calls
    for (int suffix = 0; suffix < 10; ++suffix) {
      for (long part = 0; part < EXPECTED_ITERATIONS_WITH_STANDARD_BYTE_BUFFER; ++part) {
        assertEquals(STREAM_NAME + "_0000" + suffix, FILENAME_GENERATOR.getStagingFilename());
      }
    }
    for (int suffix = 10; suffix < 20; ++suffix) {
      for (int part = 0; part < EXPECTED_ITERATIONS_WITH_STANDARD_BYTE_BUFFER; ++part) {
        assertEquals(STREAM_NAME + "_000" + suffix, FILENAME_GENERATOR.getStagingFilename());
      }
    }
  }

}
