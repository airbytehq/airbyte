/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.SystemErrorException
import io.mockk.every
import io.mockk.mockk
import java.nio.ByteBuffer
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigqueryBatchStandardInsertsLoaderTest {
    @Test
    fun `finish fails clearly when write channel returns null job after close`() {
        val writer =
            mockk<TableDataWriteChannel> {
                every { write(any<ByteBuffer>()) } returns 0
                every { close() } returns Unit
                every { job } returns null
            }
        val bigquery =
            mockk<BigQuery> {
                every { writer(any<JobId>(), any<WriteChannelConfiguration>()) } returns writer
            }
        val writeChannelConfiguration =
            WriteChannelConfiguration.newBuilder(TableId.of("dataset", "table"))
                .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
                .setFormatOptions(FormatOptions.json())
                .build()
        val loader =
            BigqueryBatchStandardInsertsLoader(
                bigquery,
                writeChannelConfiguration,
                JobId.of("project", "job"),
                mockk(),
            )

        val exception = assertThrows<SystemErrorException> { runBlocking { loader.finish() } }

        assertEquals("BigQuery load job is unavailable.", exception.message)
    }
}
