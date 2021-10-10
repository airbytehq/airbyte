package io.airbyte.integrations.destination.destination_null.logger;

import io.airbyte.protocol.models.AirbyteRecordMessage;

public interface NullDestinationLogger {

  enum LoggingType {
    NoLogging,
    FirstN,
    EveryNth,
    RandomSampling
  }

  void log(AirbyteRecordMessage recordMessage);

}
