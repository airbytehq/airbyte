/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.operation

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import java.util.*
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.reset
import org.mockito.Mockito.verifyNoMoreInteractions
import org.mockito.Mockito.`when`
import org.mockito.kotlin.any
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder

@SuppressFBWarnings("BC_IMPOSSIBLE_CAST")
class SnowflakeStorageOperationTest {
    private val sqlGenerator = mock(SnowflakeSqlGenerator::class.java)
    private val destinationHandler = mock(SnowflakeDestinationHandler::class.java)
    private val stagingClient = mock(SnowflakeStagingClient::class.java)
    private val storageOperation: SnowflakeStorageOperation =
        SnowflakeStorageOperation(sqlGenerator, destinationHandler, 1, stagingClient)

    @AfterEach
    fun tearDown() {
        reset(sqlGenerator)
        reset(destinationHandler)
        reset(stagingClient)
    }

    @Test
    fun verifyPrepareStageCreatesTableAndStage() {
        val inOrder = inOrder(destinationHandler, stagingClient)
        storageOperation.prepareStage(streamId, "", false)
        inOrder
            .verify(destinationHandler)
            .execute(Sql.of(storageOperation.createTableQuery(streamId, "")))
        inOrder
            .verify(stagingClient)
            .createStageIfNotExists(storageOperation.getStageName(streamId))
        verifyNoMoreInteractions(destinationHandler, stagingClient)
    }

    @Test
    fun verifyPrepareStageOverwriteTruncatesTable() {
        val inOrder = inOrder(destinationHandler, stagingClient)
        storageOperation.prepareStage(streamId, "", true)
        inOrder
            .verify(destinationHandler)
            .execute(Sql.of(storageOperation.createTableQuery(streamId, "")))
        inOrder
            .verify(destinationHandler)
            .execute(Sql.of(storageOperation.truncateTableQuery(streamId, "")))
        inOrder
            .verify(stagingClient)
            .createStageIfNotExists(storageOperation.getStageName(streamId))
        verifyNoMoreInteractions(destinationHandler, stagingClient)
    }

    @Test
    fun verifyWriteToStage() {
        val mockTmpFileName = "random-tmp-file-name"
        val data = mock(CsvSerializedBuffer::class.java)
        `when`(data.filename).thenReturn(mockTmpFileName)
        val stageName = storageOperation.getStageName(streamId)
        // stagingPath has UUID which isn't injected atm.
        val stagingClient = mock(SnowflakeStagingClient::class.java)
        doReturn(mockTmpFileName).`when`(stagingClient).uploadRecordsToStage(any(), any(), any())
        val storageOperation =
            SnowflakeStorageOperation(sqlGenerator, destinationHandler, 1, stagingClient)

        storageOperation.writeToStage(streamConfig, "", data)
        val inOrder = inOrder(stagingClient)
        inOrder.verify(stagingClient).uploadRecordsToStage(any(), eq(stageName), any())
        inOrder
            .verify(stagingClient)
            .copyIntoTableFromStage(
                eq(stageName),
                any(),
                eq(listOf(mockTmpFileName)),
                eq(streamId),
                eq("")
            )
        verifyNoMoreInteractions(stagingClient)
    }

    @Test
    fun verifyCleanUpStage() {
        storageOperation.cleanupStage(streamId)
        val inOrder = inOrder(stagingClient)
        inOrder.verify(stagingClient).dropStageIfExists(eq(storageOperation.getStageName(streamId)))
        verifyNoMoreInteractions(stagingClient)
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
        val streamConfig =
            StreamConfig(
                streamId,
                ImportType.APPEND,
                listOf(),
                Optional.empty(),
                linkedMapOf(),
                0,
                0,
                0,
            )
    }
}
