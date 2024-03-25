/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

class TestJdbcSqlOperations : JdbcSqlOperations() {
    @Throws(Exception::class)
    public override fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    ) {
        // Not required for the testing
    }

    @Throws(Exception::class)
    override fun insertRecordsInternalV2(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    ) {
        // Not required for the testing
    }

    @Test
    fun testCreateSchemaIfNotExists() {
        val db = Mockito.mock(JdbcDatabase::class.java)
        val schemaName = "foo"
        try {
            Mockito.doThrow(SQLException("TEST")).`when`(db).execute(Mockito.anyString())
        } catch (e: Exception) {
            // This would not be expected, but the `execute` method above will flag as an unhandled
            // exception
            assert(false)
        }
        val exception =
            Assertions.assertThrows(SQLException::class.java) {
                createSchemaIfNotExists(db, schemaName)
            }
        Assertions.assertEquals(exception.message, "TEST")
    }
}
