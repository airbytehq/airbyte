/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.operation

import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.mockk.confirmVerified
import io.mockk.every
import io.mockk.mockk
import io.mockk.verifySequence
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class SnowflakeStorageOperationTest {

    @Nested
    inner class SuccessTest {
        private val sqlGenerator = mockk<SnowflakeSqlGenerator>(relaxed = true)
        private val destinationHandler = mockk<SnowflakeDestinationHandler>(relaxed = true)
        private val stagingClient = mockk<SnowflakeStagingClient>(relaxed = true)
        private val storageOperation: SnowflakeStorageOperation =
            SnowflakeStorageOperation(sqlGenerator, destinationHandler, 1, stagingClient)
        @Test
        fun verifyPrepareStageCreatesTableAndStage() {
            storageOperation.prepareStage(streamId, DestinationSyncMode.APPEND)
            verifySequence {
                destinationHandler.execute(Sql.of(storageOperation.createTableQuery(streamId)))
                stagingClient.createStageIfNotExists(storageOperation.getStageName(streamId))
            }
            confirmVerified(destinationHandler)
            confirmVerified(stagingClient)
        }

        @Test
        fun verifyPrepareStageOverwriteTruncatesTable() {
            storageOperation.prepareStage(streamId, DestinationSyncMode.OVERWRITE)
            verifySequence {
                destinationHandler.execute(Sql.of(storageOperation.createTableQuery(streamId)))
                destinationHandler.execute(Sql.of(storageOperation.truncateTableQuery(streamId)))
                stagingClient.createStageIfNotExists(storageOperation.getStageName(streamId))
            }
            confirmVerified(destinationHandler)
            confirmVerified(stagingClient)
        }

        @Test
        fun verifyWriteToStage() {
            val mockTmpFileName = "random-tmp-file-name"
            val data = mockk<SerializableBuffer>() { every { filename } returns mockTmpFileName }
            val stageName = storageOperation.getStageName(streamId)
            // stagingPath has UUID which isn't injected atm.
            val stagingClient =
                mockk<SnowflakeStagingClient>(relaxed = true) {
                    every { uploadRecordsToStage(any(), any(), any()) } returns mockTmpFileName
                }
            val storageOperation =
                SnowflakeStorageOperation(sqlGenerator, destinationHandler, 1, stagingClient)
            storageOperation.writeToStage(streamId, data)

            verifySequence {
                stagingClient.uploadRecordsToStage(
                    data,
                    stageName,
                    any(),
                )
                stagingClient.copyIntoTableFromStage(
                    stageName,
                    any(),
                    listOf(mockTmpFileName),
                    streamId,
                )
            }
            confirmVerified(stagingClient)
        }

        @Test
        fun verifyCleanUpStage() {
            storageOperation.cleanupStage(streamId)
            verifySequence {
                stagingClient.dropStageIfExists(storageOperation.getStageName(streamId))
            }
            confirmVerified(stagingClient)
        }
    }

    companion object {
        val streamId =
            StreamId(
                "final_namespace",
                "final_name",
                "raw_namespace",
                "raw_name",
                "original_namespace",
                "original_name",
            )
    }
}
