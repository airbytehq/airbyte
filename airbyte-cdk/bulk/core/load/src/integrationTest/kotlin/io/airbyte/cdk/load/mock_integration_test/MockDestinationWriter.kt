/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.UUID
import javax.inject.Singleton
import kotlinx.coroutines.delay

@Singleton
class MockDestinationWriter : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return MockStreamLoader(stream)
    }
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class MockStreamLoader(override val stream: DestinationStream) : StreamLoader {
    private val log = KotlinLogging.logger {}

    abstract class MockBatch : Batch {
        override val groupId: String? = null
    }

    data class LocalBatch(val records: List<DestinationRecordAirbyteValue>) : MockBatch() {
        override val state = Batch.State.STAGED
    }
    data class LocalFileBatch(val file: DestinationFile) : MockBatch() {
        override val state = Batch.State.STAGED
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            when (val importType = stream.importType) {
                is Append -> {
                    MockDestinationBackend.commitFrom(
                        getFilename(stream.descriptor, staging = true),
                        getFilename(stream.descriptor)
                    )
                }
                is Dedupe -> {
                    MockDestinationBackend.commitAndDedupeFrom(
                        getFilename(stream.descriptor, staging = true),
                        getFilename(stream.descriptor),
                        importType.primaryKey,
                        importType.cursor,
                    )
                }
                else -> throw IllegalArgumentException("Unsupported import type $importType")
            }
            MockDestinationBackend.deleteOldRecords(
                getFilename(stream.descriptor),
                stream.minimumGenerationId
            )
        }
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        return LocalBatch(records.asSequence().toList())
    }

    override suspend fun processBatch(batch: Batch): Batch {
        return when (batch) {
            is LocalBatch -> {
                log.info { "Persisting ${batch.records.size} records for ${stream.descriptor}" }
                batch.records.forEach {
                    val filename = getFilename(it.stream, staging = true)
                    val record =
                        OutputRecord(
                            UUID.randomUUID(),
                            Instant.ofEpochMilli(it.emittedAtMs),
                            Instant.ofEpochMilli(System.currentTimeMillis()),
                            stream.generationId,
                            it.data as ObjectValue,
                            OutputRecord.Meta(
                                changes = it.meta?.changes ?: listOf(),
                                syncId = stream.syncId
                            ),
                        )
                    // blind insert into the staging area. We'll dedupe on commit.
                    MockDestinationBackend.insert(filename, record)
                }
                // HACK: This destination is too fast and causes a race
                // condition between consuming and flushing state messages
                // that causes the test to fail. This would not be an issue
                // in a real sync, because we would always either get more
                // data or an end-of-stream that would force a final flush.
                delay(100L)
                SimpleBatch(state = Batch.State.COMPLETE)
            }
            else -> throw IllegalStateException("Unexpected batch type: $batch")
        }
    }

    companion object {
        fun getFilename(stream: DestinationStream.Descriptor, staging: Boolean = false) =
            getFilename(stream.namespace, stream.name, staging)
        fun getFilename(namespace: String?, name: String, staging: Boolean = false) =
            if (staging) {
                "(${namespace},${name},staging)"
            } else {
                "(${namespace},${name})"
            }
    }
}
