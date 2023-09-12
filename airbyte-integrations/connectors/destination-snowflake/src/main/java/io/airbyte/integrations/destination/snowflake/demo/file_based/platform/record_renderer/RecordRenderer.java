package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

public interface RecordRenderer {
  byte[] render(AirbyteRecordMessage record);
}
