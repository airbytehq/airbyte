/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.check

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.databricks.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricks.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.airbyte.integrations.destination.databricks.spec.PersonalAccessTokenConfiguration
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows

class DatabricksCheckerTest {

    private lateinit var databricksClient: DatabricksAirbyteClient
    private lateinit var config: DatabricksConfiguration
    private lateinit var checker: DatabricksChecker

    private val metaColumnSchema =
        linkedMapOf(
            "_airbyte_raw_id" to ColumnType("STRING", false),
            "_airbyte_extracted_at" to ColumnType("TIMESTAMP", false),
            "_airbyte_meta" to ColumnType("STRING", false),
            "_airbyte_generation_id" to ColumnType("LONG", true),
        )

    @BeforeEach
    fun setup() {
        databricksClient = mockk(relaxed = true)
        config =
            DatabricksConfiguration(
                hostname = "test.cloud.databricks.com",
                httpPath = "sql/1.0/warehouses/abc123",
                port = "443",
                database = "test_catalog",
                schema = "test_schema",
                authType = PersonalAccessTokenConfiguration("test-token"),
                purgeStagingData = true,
                acceptTerms = true,
                cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            )
        checker = DatabricksChecker(databricksClient, config)
    }

    @Test
    fun `check succeeds when row count is 1`() {
        coEvery { databricksClient.createNamespace(any()) } returns Unit
        coEvery { databricksClient.createTable(any(), any(), any(), any()) } returns Unit
        every { databricksClient.describeTable(any()) } returns LinkedHashMap(metaColumnSchema)
        coEvery { databricksClient.countTable(any()) } returns 1L

        assertDoesNotThrow { checker.check() }

        coVerify(exactly = 1) { databricksClient.createNamespace("test_schema") }
        coVerify(exactly = 1) { databricksClient.createTable(any(), any(), any(), any()) }
        coVerify(exactly = 1) { databricksClient.countTable(any()) }
    }

    @Test
    fun `check fails when row count is 0`() {
        coEvery { databricksClient.createNamespace(any()) } returns Unit
        coEvery { databricksClient.createTable(any(), any(), any(), any()) } returns Unit
        every { databricksClient.describeTable(any()) } returns LinkedHashMap(metaColumnSchema)
        coEvery { databricksClient.countTable(any()) } returns 0L

        val exception = assertThrows<IllegalArgumentException> { checker.check() }

        assertTrue(exception.message!!.contains("expected 1 row"))
        assertTrue(exception.message!!.contains("got 0"))
    }

    @Test
    fun `check fails when row count is null`() {
        coEvery { databricksClient.createNamespace(any()) } returns Unit
        coEvery { databricksClient.createTable(any(), any(), any(), any()) } returns Unit
        every { databricksClient.describeTable(any()) } returns LinkedHashMap(metaColumnSchema)
        coEvery { databricksClient.countTable(any()) } returns null

        val exception = assertThrows<IllegalArgumentException> { checker.check() }

        assertTrue(exception.message!!.contains("expected 1 row"))
    }

    @Test
    fun `check propagates createNamespace failure`() {
        coEvery { databricksClient.createNamespace(any()) } throws
            RuntimeException("JDBC connection failed")

        val exception = assertThrows<RuntimeException> { checker.check() }

        assertEquals("JDBC connection failed", exception.message)
    }

    @Test
    fun `cleanup drops the check table and staging volume`() {
        coEvery { databricksClient.createNamespace(any()) } returns Unit
        coEvery { databricksClient.createTable(any(), any(), any(), any()) } returns Unit
        every { databricksClient.describeTable(any()) } returns LinkedHashMap(metaColumnSchema)
        coEvery { databricksClient.countTable(any()) } returns 1L

        checker.check()
        checker.cleanup()

        coVerify(exactly = 1) { databricksClient.dropTable(any<TableName>()) }
    }

    @Test
    fun `cleanup is safe when check was never called`() {
        assertDoesNotThrow { checker.cleanup() }

        coVerify(exactly = 0) { databricksClient.dropTable(any<TableName>()) }
    }

    @Test
    fun `check fails when terms are not accepted`() {
        val noTermsConfig = config.copy(acceptTerms = false)
        val noTermsChecker = DatabricksChecker(databricksClient, noTermsConfig)

        val exception = assertThrows<IllegalArgumentException> { noTermsChecker.check() }

        assertTrue(exception.message!!.contains("accept_terms"))
        coVerify(exactly = 0) { databricksClient.createNamespace(any()) }
    }

    @Test
    fun `check uses lowercased schema from config`() {
        val upperConfig = config.copy(schema = "MySchema")
        val upperChecker = DatabricksChecker(databricksClient, upperConfig)

        coEvery { databricksClient.createNamespace(any()) } returns Unit
        coEvery { databricksClient.createTable(any(), any(), any(), any()) } returns Unit
        every { databricksClient.describeTable(any()) } returns LinkedHashMap(metaColumnSchema)
        coEvery { databricksClient.countTable(any()) } returns 1L

        upperChecker.check()

        coVerify(exactly = 1) { databricksClient.createNamespace("myschema") }
    }
}
