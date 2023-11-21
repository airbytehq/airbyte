/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedReader;
import java.util.stream.Stream;

public interface AirbyteStreamFactory {

  Stream<AirbyteMessage> create(BufferedReader bufferedReader);

  // default Stream<io.airbyte.protocol.protos.AirbyteMessage> createProto(BufferedReader
  // bufferedReader) {
  // return Stream.of(io.airbyte.protocol.protos.AirbyteMessage.newBuilder().build());
  // }

}
