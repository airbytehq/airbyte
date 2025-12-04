/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.mockk.every
import io.mockk.mockk
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PostgresSqlGeneratorTest {

    private val namingTransformer = mockk<NamingConventionTransformer>()

    @org.junit.jupiter.api.BeforeEach
    fun setup() {
        every { namingTransformer.getIdentifier(any()) } answers { firstArg<String>() }
        every { namingTransformer.getNamespace(any()) } answers { firstArg<String>() }
        every { namingTransformer.convertStreamName(any()) } answers { firstArg<String>() }
    }

    @Test
    fun testCreateTableNormal() {
        // Setup
        val generator = PostgresSqlGenerator(namingTransformer, false, false)
        val streamId =
            StreamId("final_ns", "final_name", "raw_ns", "raw_name", "orig_ns", "orig_name")
        val streamConfig = mockk<StreamConfig>()
        every { streamConfig.id } returns streamId
        every { streamConfig.postImportAction } returns ImportType.DEDUPE
        every { streamConfig.primaryKey } returns listOf(ColumnId("pk", "pk", "pk"))
        every { streamConfig.cursor } returns Optional.of(ColumnId("cursor", "cursor", "cursor"))
        every { streamConfig.columns } returns linkedMapOf()

        // Execution
        val sql = generator.createTable(streamConfig, "", false)
        val sqlString = sql.transactions.joinToString("\n")

        // Should contain the complex index for dedupe (row_number) which includes pk and cursor
        assertTrue(sqlString.contains("\"pk\""))
        assertTrue(sqlString.contains("\"cursor\""))
    }
}
