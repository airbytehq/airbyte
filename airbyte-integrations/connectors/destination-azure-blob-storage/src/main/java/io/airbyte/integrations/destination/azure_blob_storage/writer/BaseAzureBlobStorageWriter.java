/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.writer;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The base implementation takes care of the following:
 * <ul>
 * <li>Create shared instance variables.</li>
 * <li>Create the bucket and prepare the bucket path.</li>
 * <li>Log and close the write.</li>
 * </ul>
 */
public abstract class BaseAzureBlobStorageWriter implements AzureBlobStorageWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseAzureBlobStorageWriter.class);

  protected final AzureBlobStorageDestinationConfig config;
  protected final AppendBlobClient appendBlobClient;
  protected final AirbyteStream stream;
  protected final DestinationSyncMode syncMode;

  protected BaseAzureBlobStorageWriter(final AzureBlobStorageDestinationConfig config,
                                       final AppendBlobClient appendBlobClient,
                                       final ConfiguredAirbyteStream configuredStream) {
    this.config = config;
    this.appendBlobClient = appendBlobClient;
    this.stream = configuredStream.getStream();
    this.syncMode = configuredStream.getDestinationSyncMode();
  }

  /**
   * Log and close the write.
   */
  @Override
  public void close(final boolean hasFailed) throws IOException {
    if (hasFailed) {
      LOGGER.warn("Failure detected. Aborting upload of stream '{}'...", stream.getName());
      closeWhenFail();
      LOGGER.warn("Upload of stream '{}' aborted.", stream.getName());
    } else {
      LOGGER.info("Uploading remaining data for stream '{}'.", stream.getName());
      closeWhenSucceed();
      LOGGER.info("Upload completed for stream '{}'.", stream.getName());
    }
  }

  /**
   * Operations that will run when the write succeeds.
   */
  protected void closeWhenSucceed() throws IOException {
    // Do nothing by default
  }

  /**
   * Operations that will run when the write fails.
   */
  protected void closeWhenFail() throws IOException {
    // Do nothing by default
  }

}
