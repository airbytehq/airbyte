/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.writer;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.protocol.PartialAirbyteRecordMessage;
import io.airbyte.protocol.models.Jsons;
import java.io.IOException;
import java.util.UUID;

/**
 * {@link DestinationWriter} is responsible for writing Airbyte stream data to an S3 location in a
 * specific format.
 */
public interface DestinationWriter {

  /**
   * Prepare an S3 writer for the stream.
   */
  void initialize() throws IOException;

  /**
   * Write an Airbyte record message to an S3 object.
   */
  void write(UUID id, PartialAirbyteRecordMessage recordMessage) throws IOException;

  default void write(final JsonNode formattedData) throws IOException {
    write(Jsons.serialize(formattedData));
  }

  void write(final String formattedData) throws IOException;

  /**
   * Close the S3 writer for the stream.
   */
  void close(boolean hasFailed) throws IOException;

  default void closeAfterPush() throws IOException {
    close(false);
  }

}
