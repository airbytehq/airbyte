/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Paths
import java.sql.SQLException
import javax.sql.DataSource
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeDestinationIntegrationTest {
    private val namingResolver = SnowflakeSQLNameTransformer()

    @BeforeEach
    fun setup() {
        DestinationConfig.initialize(emptyObject())
    }

    @Test
    @Throws(Exception::class)
    fun testCheckFailsWithInvalidPermissions() {
        // TODO(sherifnada) this test case is assumes config.json does not have permission to access
        // the
        // schema
        // this connector should be updated with multiple credentials, each with a clear purpose
        // (valid,
        // invalid: insufficient permissions, invalid: wrong password, etc..)
        val credentialsJsonString = deserialize(Files.readString(Paths.get("secrets/config.json")))
        val check =
            SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS).check(credentialsJsonString)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, check!!.status)
    }

    @Test
    fun testCheckSuccessTest() {
        val credentialsJsonString =
            deserialize(Files.readString(Paths.get("secrets/1s1t_internal_staging_config.json")))
        val check =
            SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS).check(credentialsJsonString)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check!!.status)
    }

    @Test
    @Throws(Exception::class)
    fun testInvalidSchemaName() {
        val config = config
        val schema = config["schema"].asText()
        val dataSource: DataSource =
            SnowflakeDatabaseUtils.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
        try {
            val database = SnowflakeDatabaseUtils.getDatabase(dataSource)
            Assertions.assertDoesNotThrow { syncWithNamingResolver(database, schema) }
            Assertions.assertThrows(SQLException::class.java) {
                syncWithoutNamingResolver(database, schema)
            }
        } finally {
            close(dataSource)
        }
    }

    @Throws(SQLException::class)
    fun syncWithNamingResolver(database: JdbcDatabase, schema: String) {
        val normalizedSchemaName = namingResolver.getIdentifier(schema)
        try {
            database.execute(String.format("CREATE SCHEMA %s", normalizedSchemaName))
        } finally {
            database.execute(String.format("DROP SCHEMA IF EXISTS %s", normalizedSchemaName))
        }
    }

    @Throws(SQLException::class)
    private fun syncWithoutNamingResolver(database: JdbcDatabase, schema: String) {
        try {
            database.execute(String.format("CREATE SCHEMA %s", schema))
        } finally {
            database.execute(String.format("DROP SCHEMA IF EXISTS %s", schema))
        }
    }

    @get:Throws(IOException::class)
    private val config: JsonNode
        get() {
            val config = deserialize(Files.readString(Paths.get("secrets/insert_config.json")))
            val schemaName =
                "schemaName with whitespace " + addRandomSuffix("integration_test", "_", 5)
            (config as ObjectNode).put("schema", schemaName)
            return config
        }
}
