/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file;

public enum UploaderType {
  STANDARD,
  JSONL,
  CSV
}
