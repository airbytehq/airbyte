/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.v0.AirbyteMessage
import java.io.BufferedReader
import java.util.stream.Stream

interface AirbyteStreamFactory {
    fun create(bufferedReader: BufferedReader): Stream<AirbyteMessage>
}
