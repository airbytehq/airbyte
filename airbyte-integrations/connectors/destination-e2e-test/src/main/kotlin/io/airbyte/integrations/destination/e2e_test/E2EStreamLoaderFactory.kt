/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.SimpleBatch
import io.airbyte.cdk.write.StreamLoader
import io.airbyte.cdk.write.StreamLoaderFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.delay

@Singleton
class E2EStreamLoaderFactory(private val config: E2EDestinationConfiguration) :
    StreamLoaderFactory {

    override fun make(stream: DestinationStream): StreamLoader {
        return when (config.testDestination) {
            is LoggingDestination ->
                LoggingStreamLoader(stream, config.testDestination.loggingConfig)
            is SilentDestination -> SilentStreamLoader(stream)
            is ThrottledDestination ->
                ThrottledStreamLoader(stream, config.testDestination.millisPerRecord)
            is FailingDestination -> FailingStreamLoader(stream, config.testDestination.numMessages)
        }
    }
}

class LoggingStreamLoader(override val stream: DestinationStream, loggingConfig: LoggingConfig) :
    StreamLoader {
    private val log = KotlinLogging.logger {}

    private val maxEntryCount: Int
    private val logEvery: Int
    private val sampleRate: Double

    init {
        when (loggingConfig) {
            is FirstNEntriesConfig -> {
                maxEntryCount = loggingConfig.maxEntryCount
                logEvery = 1
                sampleRate = 1.0
            }
            is EveryNthEntryConfig -> {
                maxEntryCount = loggingConfig.maxEntryCount
                logEvery = loggingConfig.nthEntryToLog
                sampleRate = 1.0
            }
            is RandomSamplingConfig -> {
                maxEntryCount = loggingConfig.maxEntryCount
                logEvery = 1
                sampleRate = loggingConfig.samplingRatio
            }
        }
    }

    companion object {
        private val recordCount = AtomicLong()
        private val logCount = AtomicLong()
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        log.info { "Processing record batch with logging" }

        records.forEach { record ->
            println("record: $record")
            if (recordCount.getAndIncrement() % logEvery == 0L) {
                if (Math.random() < sampleRate) {
                    if (logCount.incrementAndGet() < maxEntryCount) {
                        log.info {
                            "Logging Destination(stream=${stream.descriptor}, recordIndex=$recordCount, logEntry=$logCount/$maxEntryCount): $record"
                        }
                    }
                }
            }
        }

        log.info { "Completed record batch." }

        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}

class SilentStreamLoader(override val stream: DestinationStream) : StreamLoader {
    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}

class ThrottledStreamLoader(
    override val stream: DestinationStream,
    private val millisPerRecord: Long
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        log.info { "Processing record batch with delay of $millisPerRecord per record" }

        records.forEach { _ -> delay(millisPerRecord) }
        log.info { "Completed record batch." }

        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}

class FailingStreamLoader(override val stream: DestinationStream, private val numMessages: Int) :
    StreamLoader {
    private val log = KotlinLogging.logger {}

    companion object {
        private val messageCount = AtomicInteger(0)
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        log.info { "Processing record batch with failure after $numMessages messages" }

        records.forEach { record ->
            messageCount.getAndIncrement().let { messageCount ->
                if (messageCount > numMessages) {
                    val message =
                        "Failing Destination(stream=${stream.descriptor}, numMessages=$numMessages: failing at $record"
                    log.info { message }
                    throw RuntimeException(message)
                }
            }
        }
        log.info { "Completed record batch." }

        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}
