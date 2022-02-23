/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import static org.junit.jupiter.api.Assertions.*;

import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

class StagingFilenameGeneratorTest {

  private static final String STREAM_NAME = RandomStringUtils.randomAlphabetic(5).toLowerCase();
  private static final int MAX_PARTS_PER_FILE = 3;
  private static final StagingFilenameGenerator FILENAME_GENERATOR =
      new StagingFilenameGenerator(STREAM_NAME, MAX_PARTS_PER_FILE);

  @Test
  public void testGetStagingFilename() {
    // the file suffix increments after every MAX_PARTS_PER_FILE method calls
    for (int suffix = 0; suffix < 10; ++suffix) {
      for (int part = 0; part < MAX_PARTS_PER_FILE; ++part) {
        assertEquals(STREAM_NAME + "_0000" + suffix, FILENAME_GENERATOR.getStagingFilename());
      }
    }
    for (int suffix = 10; suffix < 20; ++suffix) {
      for (int part = 0; part < MAX_PARTS_PER_FILE; ++part) {
        assertEquals(STREAM_NAME + "_000" + suffix, FILENAME_GENERATOR.getStagingFilename());
      }
    }
  }

}
