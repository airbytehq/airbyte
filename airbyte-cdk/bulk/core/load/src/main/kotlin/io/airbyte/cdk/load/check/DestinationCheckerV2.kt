/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.WriteOperation
import java.io.InputStream
import java.io.PipedInputStream
import java.io.PipedOutputStream
import java.io.PrintWriter
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

/**
 * A check operation that is run before the destination is used.
 *
 * * Implementors must provide a [check] method that validates the configuration.
 * * Implementors may provide a [cleanup] method that is run after the check is complete.
 * * [check] should throw an exception if the configuration is invalid.
 * * [cleanup] should not throw exceptions.
 * * Implementors should not perform any side effects in the constructor.
 * * Implementors should not throw exceptions in the constructor.
 * * Implementors should not inject configuration; only use the config passed in [check].
 */
interface DestinationCheckerV2 {
    fun check()
    fun cleanup() {}
}

class DestinationCheckerSyncV2(
    val catalog: DestinationCatalog,
    stdinPipe: InputStream,
    private val writeOperation: WriteOperation,
    private val cleaner: CheckCleanerV2,
) : DestinationCheckerV2 {
    private val pipe: PrintWriter

    init {
        // See InputStreamProvider.make - in a CHECK operation, we swap the inputstream
        // with a PipedInputStream.
        val stdinPipeOutputStream = PipedOutputStream(stdinPipe as PipedInputStream)
        pipe = PrintWriter(stdinPipeOutputStream)
    }

    override fun check() {
        check(catalog.streams.size == 1) { "test catalog should have exactly 1 stream" }
        val mockStream = catalog.streams.first()
        runBlocking(Dispatchers.IO) {
            launch { writeOperation.execute() }

            pipe.println(
                InputRecord(
                        mockStream,
                        """{"test": 42}""",
                        System.currentTimeMillis(),
                    )
                    .asProtocolMessage()
                    .serializeToString()
            )
            pipe.println(
                DestinationRecordStreamComplete(mockStream, System.currentTimeMillis())
                    .asProtocolMessage()
                    .serializeToString()
            )
            pipe.close()
        }
    }

    override fun cleanup() {
        catalog.streams.forEach { stream -> cleaner.cleanup(stream) }
    }
}

// TODO the cleaner maybe should also be looking for old test tables, a la DestinationCleaner??
fun interface CheckCleanerV2 {
    fun cleanup(stream: DestinationStream)
}
