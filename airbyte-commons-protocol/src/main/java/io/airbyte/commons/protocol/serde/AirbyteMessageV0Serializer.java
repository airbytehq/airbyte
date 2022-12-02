/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.serde;

import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Singleton;

@Singleton
public class AirbyteMessageV0Serializer extends AirbyteMessageGenericSerializer<AirbyteMessage> {

  public AirbyteMessageV0Serializer() {
    super(AirbyteProtocolVersion.V0);
  }

}
