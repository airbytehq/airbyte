/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects;

import io.airbyte.protocol.models.AirbyteTraceMessage;

public interface AirbyteMessage {

  AirbyteMessageType getType();

  ConnectorSpecification getSpec();

  // TODO should be an interface
  AirbyteTraceMessage getTrace();

}
