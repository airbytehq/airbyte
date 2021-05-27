package io.airbyte.integrations.destination.s3;

import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.IOException;
import java.util.UUID;

public interface S3Handler {

  void initialize() throws IOException;

  void write(UUID id, AirbyteRecordMessage recordMessage) throws IOException;

  void close(boolean hasFailed) throws IOException;

}
