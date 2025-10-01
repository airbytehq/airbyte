/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.DEFAULT_COLUMNS
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeCheckerTest {

    @ParameterizedTest
    @ValueSource(booleans = [true, false])
    fun testSuccessfulCheck(isLegacyRawTablesOnly: Boolean) {
        val snowflakeAirbyteClient: SnowflakeAirbyteClient =
            mockk(relaxed = true) { coEvery { countTable(any()) } returns 1L }

        val testSchema = "test-schema"
        val snowflakeConfiguration: SnowflakeConfiguration = mockk {
            every { schema } returns testSchema
            every { legacyRawTablesOnly } returns isLegacyRawTablesOnly
        }
        val snowflakeColumnUtils =
            mockk<SnowflakeColumnUtils>(relaxUnitFun = true) {
                every { getFormattedDefaultColumnNames(any()) } returns
                    DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }
            }

        val checker =
            SnowflakeChecker(
                snowflakeAirbyteClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )
        checker.check()

        coVerify(exactly = 1) {
            snowflakeAirbyteClient.createNamespace(testSchema.toSnowflakeCompatibleName())
        }
        coVerify(exactly = 1) { snowflakeAirbyteClient.createTable(any(), any(), any(), any()) }
        coVerify(exactly = 1) { snowflakeAirbyteClient.dropTable(any()) }
    }

    @ParameterizedTest
    @ValueSource(booleans = [true, false])
    fun testUnsuccessfulCheck(isLegacyRawTablesOnly: Boolean) {
        val snowflakeAirbyteClient: SnowflakeAirbyteClient =
            mockk(relaxed = true) { coEvery { countTable(any()) } returns 0L }

        val testSchema = "test-schema"
        val snowflakeConfiguration: SnowflakeConfiguration = mockk {
            every { schema } returns testSchema
            every { legacyRawTablesOnly } returns isLegacyRawTablesOnly
        }
        val snowflakeColumnUtils =
            mockk<SnowflakeColumnUtils>(relaxUnitFun = true) {
                every { getFormattedDefaultColumnNames(any()) } returns
                    DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }
            }

        val checker =
            SnowflakeChecker(
                snowflakeAirbyteClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )

        assertThrows<IllegalArgumentException> { checker.check() }

        coVerify(exactly = 1) {
            snowflakeAirbyteClient.createNamespace(testSchema.toSnowflakeCompatibleName())
        }
        coVerify(exactly = 1) { snowflakeAirbyteClient.createTable(any(), any(), any(), any()) }
        coVerify(exactly = 1) { snowflakeAirbyteClient.dropTable(any()) }
    }
}
