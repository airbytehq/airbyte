/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.protocol.models.v0.AirbyteMessage;

public class AirbyteMessageDeserializerV0 implements AirbyteMessageDeserializer<AirbyteMessage> {

  @Override
  public AirbyteMessage deserialize(JsonNode json) {
    return Jsons.object(json, AirbyteMessage.class);
  }

  @Override
  public AirbyteVersion getTargetVersion() {
    return new AirbyteVersion("0.3.0");
  }

}
