/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.json.Jsons.emptyObject
import java.sql.Connection
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.mockito.Mockito.mock
import org.mockito.kotlin.any

internal class SnowflakeSqlOperationsTest {
    private var snowflakeSqlOperations: SnowflakeSqlOperations? = null
    var db: JdbcDatabase = mock()

    @BeforeEach
    fun setup() {
        DestinationConfig.initialize(emptyObject())
        snowflakeSqlOperations = SnowflakeSqlOperations()
    }

    @Test
    fun createTableQuery() {
        val expectedQuery =
            String.format(
                """
        CREATE TABLE IF NOT EXISTS "%s"."%s" (
          "%s" VARCHAR PRIMARY KEY,
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
          "%s" VARIANT
        ) data_retention_time_in_days = 1;
        """.trimIndent(),
                SCHEMA_NAME,
                TABLE_NAME,
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
                JavaBaseConstants.COLUMN_NAME_DATA
            )
        val actualQuery = snowflakeSqlOperations!!.createTableQuery(SCHEMA_NAME, TABLE_NAME)
        Assertions.assertEquals(expectedQuery, actualQuery)
    }

    @Throws(Exception::class)
    @Test
    fun testSchemaExists() {
        snowflakeSqlOperations!!.isSchemaExists(db, SCHEMA_NAME)
        Mockito.verify(db, Mockito.times(1)).unsafeQuery(ArgumentMatchers.anyString())
    }

    @Test
    @Throws(SQLException::class)
    @SuppressFBWarnings("BC_IMPOSSIBLE_CAST")
    fun insertRecordsInternal() {
        snowflakeSqlOperations!!.insertRecordsInternal(
            db,
            listOf(PartialAirbyteMessage()),
            SCHEMA_NAME,
            TABLE_NAME
        )
        Mockito.verify(db, Mockito.times(1))
            .execute(any<CheckedConsumer<Connection, SQLException>>())
    }

    companion object {
        var SCHEMA_NAME: String = "schemaName"
        const val TABLE_NAME: String = "tableName"
    }
}
