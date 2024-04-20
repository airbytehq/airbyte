/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import java.io.BufferedWriter

interface AirbyteMessageBufferedWriterFactory {
    fun createWriter(bufferedWriter: BufferedWriter): AirbyteMessageBufferedWriter
}
