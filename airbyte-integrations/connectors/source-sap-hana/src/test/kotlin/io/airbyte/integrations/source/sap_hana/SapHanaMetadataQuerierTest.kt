/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import java.sql.SQLException
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class SapHanaMetadataQuerierTest {
    var db =
        SapHanaTestDatabase(
            "1bd5e6cf-2112-4b8d-b9d2-3ea58d8a6a8e.hna0.prod-us10.hanacloud.ondemand.com",
            443,
            "DBADMIN",
            "Dbsource12345!"
        )

    val hanaQuerierFactory =
        SapHanaSourceMetadataQuerier.Factory(
            selectQueryGenerator = SapHanaSourceOperations(),
            fieldTypeMapper = SapHanaSourceOperations(),
            checkQueries = JdbcCheckQueries(),
            constants = DefaultJdbcConstants(),
        )

    // create two random schema and table names. These will be used to test the querier.
    val schemaNames = db.getRandomSchemaNames(2)
    val tableNames = db.getRandomTableNames(2)

    val configPojo =
        SapHanaSourceConfigurationSpecification().apply {
            port = db.port
            host = db.host
            schemas = schemaNames
            username = db.username
            password = db.password
        }

    @BeforeEach
    fun setUp() {
        try {
            db.connect()
            for (i in 0..schemaNames.size - 1) {
                db.execute("CREATE SCHEMA ${schemaNames[i]}")
                for (j in 0..tableNames.size - 1) {
                    db.execute(
                        "CREATE TABLE ${schemaNames[i]}.${tableNames[j]} (ID INT PRIMARY KEY, NAME VARCHAR(255))"
                    )
                }
            }
        } catch (e: SQLException) {
            e.printStackTrace()
        }
    }

    @AfterEach
    fun tearDown() {
        try {
            for (i in 0..schemaNames.size - 1) db.execute("DROP SCHEMA ${schemaNames[i]} CASCADE")
            db.disconnect()
        } catch (e: SQLException) {
            e.printStackTrace()
        }
    }

    @Test
    fun testsGetStreamNameSpaces() {
        val config: SapHanaSourceConfiguration =
            SapHanaSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        assertEquals(
            schemaNames.toSet(),
            hanaQuerierFactory.session(config).streamNamespaces().toSet()
        )
    }

    @Test
    fun testStreamNames() {
        val config: SapHanaSourceConfiguration =
            SapHanaSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        schemaNames.forEach {
            assertEquals(
                tableNames.toSet(),
                // get the stream names without the schema name being the prefix
                hanaQuerierFactory
                    .session(config)
                    .streamNames(it)
                    .map { stream -> stream.name }
                    .toSet()
            )
        }
    }

    @Test
    fun testFields() {
        val config: SapHanaSourceConfiguration =
            SapHanaSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        schemaNames.forEach { schema ->
            val stream_ids = hanaQuerierFactory.session(config).streamNames(schema)
            for (stream_id in stream_ids) {
                val fields = hanaQuerierFactory.session(config).fields(stream_id)
                assertEquals(2, fields.size)
                assertEquals("ID", fields[0].id.toString())
                assertEquals("IntFieldType", fields[0].type.toString())
                assertEquals("NAME", fields[1].id.toString())
                assertEquals("NStringFieldType", fields[1].type.toString())
            }
        }
    }

    @Test
    fun testPrimaryKey() {
        val config: SapHanaSourceConfiguration =
            SapHanaSourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        schemaNames.forEach { schema ->
            val stream_ids = hanaQuerierFactory.session(config).streamNames(schema)
            for (stream_id in stream_ids) {
                val pk = hanaQuerierFactory.session(config).primaryKey(stream_id)
                assertEquals(1, pk.size)
                assertEquals("ID", pk[0][0])
            }
        }
    }
}
