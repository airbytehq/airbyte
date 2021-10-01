/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedReader;
import java.util.stream.Stream;

public interface AirbyteStreamFactory {

  Stream<AirbyteMessage> create(BufferedReader bufferedReader);

}
