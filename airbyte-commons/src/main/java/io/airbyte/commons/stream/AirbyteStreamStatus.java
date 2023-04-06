/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;

/**
 * Represents the current status of a stream provided by a source.
 */
public class AirbyteStreamStatus {

  private final AirbyteStreamNameNamespacePair airbyteStream;

  // TODO This wil include the protocol stream status enum value of the message to be created as well
  // as the stream information

  public AirbyteStreamStatus(final AirbyteStreamNameNamespacePair airbyteStream) {
    this.airbyteStream = airbyteStream;
  }

  public AirbyteStreamNameNamespacePair getAirbyteStream() {
    return airbyteStream;
  }

}
