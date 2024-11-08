/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import java.time.Instant
import java.util.UUID
import javax.inject.Singleton

@Singleton
class MockDestinationWriter : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return MockStreamLoader(stream)
    }
}

class MockStreamLoader(override val stream: DestinationStream) : StreamLoader {
    data class LocalBatch(val records: List<DestinationRecord>) : Batch {
        override val state = Batch.State.LOCAL
    }
    data class PersistedBatch(val records: List<DestinationRecord>) : Batch {
        override val state = Batch.State.PERSISTED
    }

    override suspend fun close(streamFailure: StreamIncompleteResult?) {
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
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        return LocalBatch(records.asSequence().toList())
    }

    override suspend fun processBatch(batch: Batch): Batch {
        return when (batch) {
            is LocalBatch -> {
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
                PersistedBatch(batch.records)
            }
            is PersistedBatch -> SimpleBatch(state = Batch.State.COMPLETE)
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
