/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

public enum S3Format {

  AVRO("avro"),
  CSV("csv"),
  JSONL("jsonl"),
  PARQUET("parquet");

  private final String fileExtension;

  S3Format(final String fileExtension) {
    this.fileExtension = fileExtension;
  }

  public String getFileExtension() {
    return fileExtension;
  }

}
