/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

public enum AzureBlobStorageFormat {

  CSV("csv"),
  JSONL("jsonl");

  private final String fileExtension;

  AzureBlobStorageFormat(String fileExtension) {
    this.fileExtension = fileExtension;
  }

  public String getFileExtension() {
    return fileExtension;
  }

}
