/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

/**
 * The staging file is uploaded to cloud storage in multiple parts. This class keeps track of the
 * filename, and returns a new one when the old file has had enough parts.
 */
public class StagingFilenameGenerator {

  private final String streamName;
  private final int maxPartsPerFile;

  // the file suffix will change after the max number of file
  // parts have been generated for the current suffix;
  // its value starts from 0.
  private int currentFileSuffix = 0;
  // the number of parts that have been generated for the current
  // file suffix; its value range will be [1, maxPartsPerFile]
  private int currentFileSuffixPartCount = 0;

  public StagingFilenameGenerator(final String streamName, final int maxPartsPerFile) {
    this.streamName = streamName;
    this.maxPartsPerFile = maxPartsPerFile;
  }

  /**
   * This method is assumed to be called whenever one part of a file is going to be created. The
   * currentFileSuffix increments from 0. The currentFileSuffixPartCount cycles from 1 to
   * maxPartsPerFile.
   */
  public String getStagingFilename() {
    if (currentFileSuffixPartCount < maxPartsPerFile) {
      // when the number of parts for the file has not reached the max,
      // keep using the same file (i.e. keep the suffix)
      currentFileSuffixPartCount += 1;
    } else {
      // otherwise, reset the part counter, and use a different file
      // (i.e. update the suffix)
      currentFileSuffix += 1;
      currentFileSuffixPartCount = 1;
    }
    return String.format("%s_%05d", streamName, currentFileSuffix);
  }

}
