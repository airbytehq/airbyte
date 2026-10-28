/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.assumeConfigured
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.connect
import java.sql.Connection
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.extension.ExtendWith

/**
 * Points the test class at the seeded [SnowflakeSharedSchema], which is created once per JVM and
 * dropped after the last test. Each class gets its own admin connection for DDL/DML, since JDBC
 * connections are not safe to share between concurrently running classes.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@ExtendWith(SnowflakeSharedSchemaExtension::class)
abstract class AbstractSnowflakeLiveTest {
    protected lateinit var schema: String
    protected lateinit var database: String
    private var adminConnection: Connection? = null

    protected val admin: Connection
        get() = adminConnection ?: error("not connected")

    protected fun spec(
        concurrency: Int? = null,
        checkpointSeconds: Int? = null,
        checkPrivileges: Boolean? = null,
        sessionTimezone: String? = "UTC",
    ): SnowflakeSourceConfigurationSpecification =
        SnowflakeLiveTestSupport.spec(
            schema = schema,
            concurrency = concurrency,
            checkpointSeconds = checkpointSeconds,
            checkPrivileges = checkPrivileges,
            sessionTimezone = sessionTimezone,
        )

    @BeforeAll
    fun useSharedSchema() {
        assumeConfigured()
        schema = SnowflakeSharedSchema.name
        database = SnowflakeSharedSchema.database
        adminConnection = connect(SnowflakeLiveTestSupport.spec(sessionTimezone = null))
    }

    @AfterAll
    fun closeAdminConnection() {
        adminConnection?.close()
    }
}
