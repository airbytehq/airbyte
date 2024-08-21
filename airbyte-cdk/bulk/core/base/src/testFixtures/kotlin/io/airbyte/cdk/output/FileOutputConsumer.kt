/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.io.FileOutputStream
import java.nio.file.Path
import java.time.Clock
import java.time.Instant

/**
 * [OutputConsumer] implementation for CLI integration tests. Writes [AirbyteMessage]s to a file
 * instead of stdout.
 */
@Singleton
@Requires(env = [Environment.TEST, Environment.CLI])
@Requires(property = CONNECTOR_OUTPUT_FILE)
@Replaces(OutputConsumer::class)
class FileOutputConsumer(
    @Value("\${$CONNECTOR_OUTPUT_FILE}") filePath: Path,
    clock: Clock,
) : OutputConsumer {
    private val writer = FileOutputStream(filePath.toFile()).bufferedWriter()

    override val emittedAt: Instant = Instant.now(clock)

    override fun accept(msg: AirbyteMessage) {
        synchronized(this) {
            writer.appendLine(Jsons.writeValueAsString(msg))
            writer.flush()
        }
    }

    override fun close() {
        synchronized(this) { writer.close() }
    }
}
