/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.assumeConfigured
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.connect
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.execute
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.executeScript
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.newSchemaName
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.TestInstance

/**
 * Creates a private schema in the configured database, seeds it from a resource script and drops it
 * afterwards. Each test class gets its own schema, so classes can run in any order.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
abstract class AbstractSnowflakeLiveTest {
    private val log = KotlinLogging.logger {}

    protected lateinit var schema: String
    protected lateinit var database: String
    private var adminConnection: Connection? = null

    protected val admin: Connection
        get() = adminConnection ?: error("schema not created")

    /** Resource script executed after the schema exists; `null` for an empty schema. */
    protected open val seedResource: String? = "seed.sql"

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
    fun createAndSeedSchema() {
        assumeConfigured()
        schema = newSchemaName()
        val baseSpec = SnowflakeLiveTestSupport.spec(sessionTimezone = null)
        database = baseSpec.database
        val conn = connect(baseSpec)
        adminConnection = conn
        log.info { "Creating test schema $database.$schema" }
        execute(conn, "CREATE SCHEMA \"$database\".\"$schema\"")
        seedResource?.let { executeScript(conn, it, mapOf("DB" to database, "SCHEMA" to schema)) }
    }

    @AfterAll
    fun dropSchema() {
        val conn = adminConnection ?: return
        try {
            execute(conn, "DROP SCHEMA IF EXISTS \"$database\".\"$schema\" CASCADE")
            log.info { "Dropped test schema $database.$schema" }
        } finally {
            conn.close()
        }
    }
}
