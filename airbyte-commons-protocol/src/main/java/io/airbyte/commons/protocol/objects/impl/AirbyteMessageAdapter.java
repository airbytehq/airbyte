/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects.impl;

import io.airbyte.commons.protocol.objects.AirbyteMessage;
import io.airbyte.commons.protocol.objects.AirbyteMessageType;
import io.airbyte.commons.protocol.objects.ConnectorSpecification;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.util.Map;

public class AirbyteMessageAdapter implements AirbyteMessage {

  private final io.airbyte.protocol.models.AirbyteMessage airbyteMessage;

  public AirbyteMessageAdapter(final io.airbyte.protocol.models.AirbyteMessage airbyteMessage) {
    this.airbyteMessage = airbyteMessage;
  }

  @Override
  public AirbyteMessageType getType() {
    return toTypes.get(airbyteMessage.getType());
  }

  @Override
  public ConnectorSpecification getSpec() {
    return null;
  }

  @Override
  public AirbyteTraceMessage getTrace() {
    return airbyteMessage.getTrace();
  }

  private final static Map<io.airbyte.protocol.models.AirbyteMessage.Type, AirbyteMessageType> toTypes = Map.of(
      Type.RECORD, AirbyteMessageType.RECORD,
      Type.STATE, AirbyteMessageType.STATE,
      Type.LOG, AirbyteMessageType.RECORD,
      Type.CONNECTION_STATUS, AirbyteMessageType.CONNECTION_STATUS,
      Type.CATALOG, AirbyteMessageType.CATALOG,
      Type.TRACE, AirbyteMessageType.TRACE,
      Type.SPEC, AirbyteMessageType.SPEC,
      Type.CONTROL, AirbyteMessageType.CONTROL);

}
