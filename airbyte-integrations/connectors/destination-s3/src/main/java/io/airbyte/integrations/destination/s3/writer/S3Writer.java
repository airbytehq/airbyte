/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.IOException;
import java.util.UUID;

/**
 * {@link S3Writer} is responsible for writing Airbyte stream data to an S3 location in a specific
 * format.
 */
public interface S3Writer {

  /**
   * Prepare an S3 writer for the stream.
   */
  void initialize() throws IOException;

  /**
   * Write an Airbyte record message to an S3 object.
   */
  void write(UUID id, AirbyteRecordMessage recordMessage) throws IOException;

  /**
   * Close the S3 writer for the stream.
   */
  void close(boolean hasFailed) throws IOException;

}
