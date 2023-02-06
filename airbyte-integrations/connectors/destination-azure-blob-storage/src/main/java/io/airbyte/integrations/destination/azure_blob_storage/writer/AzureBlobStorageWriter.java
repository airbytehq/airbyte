/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.writer;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.IOException;
import java.util.UUID;

/**
 * {@link AzureBlobStorageWriter} is responsible for writing Airbyte stream data to an
 * AzureBlobStorage location in a specific format.
 */
public interface AzureBlobStorageWriter {

  /**
   * Write an Airbyte record message to an AzureBlobStorage object.
   */
  void write(UUID id, AirbyteRecordMessage recordMessage) throws IOException;

  /**
   * Close the AzureBlobStorage writer for the stream.
   */
  void close(boolean hasFailed) throws IOException;

}
