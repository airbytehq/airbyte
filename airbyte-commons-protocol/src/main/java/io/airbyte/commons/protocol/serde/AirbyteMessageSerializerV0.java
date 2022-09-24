/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.protocol.models.v0.AirbyteMessage;

public class AirbyteMessageSerializerV0 implements AirbyteMessageSerializer<AirbyteMessage> {

  @Override
  public String serialize(AirbyteMessage message) {
    return Jsons.serialize(message);
  }

  @Override
  public AirbyteVersion getTargetVersion() {
    return new AirbyteVersion("0.3.0");
  }

}
