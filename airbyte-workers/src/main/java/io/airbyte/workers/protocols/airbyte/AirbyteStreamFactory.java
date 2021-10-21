/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.Application;
import java.io.BufferedReader;
import java.util.stream.Stream;

public interface AirbyteStreamFactory extends Application {

  Stream<AirbyteMessage> create(BufferedReader bufferedReader);

}
