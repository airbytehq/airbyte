/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import io.airbyte.protocol.models.AirbyteMessage
import java.io.BufferedReader
import java.util.stream.Stream

interface AirbyteStreamFactory {
    fun create(bufferedReader: BufferedReader): Stream<AirbyteMessage>
}
