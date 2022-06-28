/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

public enum CompressionType {

  NO_COMPRESSION(""),
  GZIP(".gz");

  private final String fileExtension;

  CompressionType(final String fileExtension) {
    this.fileExtension = fileExtension;
  }

  public String getFileExtension() {
    return fileExtension;
  }

}
