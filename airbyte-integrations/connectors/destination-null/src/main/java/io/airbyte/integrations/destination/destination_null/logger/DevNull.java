package io.airbyte.integrations.destination.destination_null.logger;

import io.airbyte.protocol.models.AirbyteRecordMessage;

public class DevNull implements NullDestinationLogger {

  public static final DevNull SINGLETON = new DevNull();

  private DevNull() {
  }

  @Override
  public void log(AirbyteRecordMessage recordMessage) {
    // nothing happens in /dev/null
  }

}
