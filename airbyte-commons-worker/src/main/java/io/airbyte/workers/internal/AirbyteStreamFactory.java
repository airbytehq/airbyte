/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedReader;
import java.util.stream.Stream;
import reactor.core.publisher.Flux;

public interface AirbyteStreamFactory {

  Flux<AirbyteMessage> createFlux(BufferedReader bufferedReader);

  Stream<AirbyteMessage> create(BufferedReader bufferedReader);

}
