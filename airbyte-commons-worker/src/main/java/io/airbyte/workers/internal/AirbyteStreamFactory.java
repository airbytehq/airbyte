/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.protocol.models.v1.AirbyteMessage;
import java.io.BufferedReader;
import java.util.stream.Stream;

public interface AirbyteStreamFactory {

  Stream<AirbyteMessage> create(BufferedReader bufferedReader);

}
