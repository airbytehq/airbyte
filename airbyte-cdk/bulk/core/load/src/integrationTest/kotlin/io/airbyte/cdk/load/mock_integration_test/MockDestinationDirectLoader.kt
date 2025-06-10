/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.test.mock.MockDestinationBackend
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.airbyte.cdk.load.test.mock.MockDestinationDataDumper.getFilename
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.time.Instant
import java.util.UUID
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking

@Singleton
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationDirectLoaderFactory : DirectLoaderFactory<MockDestinationDirectLoader> {
    override fun create(streamDescriptor: DestinationStream.Descriptor, part: Int) =
        MockDestinationDirectLoader()
}

class MockDestinationDirectLoader : DirectLoader {
    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val recordAirbyteValue = record.asDestinationRecordAirbyteValue()
        val filename = getFilename(record.stream.descriptor, staging = true)
        val outputRecord =
            OutputRecord(
                UUID.randomUUID(),
                Instant.ofEpochMilli(recordAirbyteValue.emittedAtMs),
                Instant.ofEpochMilli(System.currentTimeMillis()),
                record.stream.generationId,
                recordAirbyteValue.data as ObjectValue,
                OutputRecord.Meta(
                    changes = recordAirbyteValue.meta?.changes ?: listOf(),
                    syncId = record.stream.syncId
                ),
            )
        // blind insert into the staging area. We'll dedupe on commit.
        MockDestinationBackend.insert(filename, outputRecord)

        // HACK: This destination is too fast and causes a race
        // condition between consuming and flushing state messages
        // that causes the test to fail. This would not be an issue
        // in a real sync, because we would always either get more
        // data or an end-of-stream that would force a final flush.
        runBlocking { delay(100L) }

        // records are immediately committed, so we can return Complete on every record
        return DirectLoader.Complete
    }

    override suspend fun finish() {
        // do nothing
    }

    override fun close() {
        // do nothing
    }
}
