/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.connect
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.execute
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.executeScript
import io.airbyte.integrations.source.snowflake.SnowflakeLiveTestSupport.newSchemaName
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.extension.BeforeAllCallback
import org.junit.jupiter.api.extension.ExtensionContext

/**
 * The one schema that every live test class in this JVM reads from: created and seeded from
 * `seed.sql` on first use, dropped by [SnowflakeSharedSchemaExtension] after the last test.
 *
 * Sharing is safe because the suite is read-mostly. The cursor tests insert into their own `INC_*`
 * tables, which no other class asserts row counts on, and the discover test creates and drops its
 * own extra schemas. Everything a class needs, including the `*_DEFAULT_TZ` copies the cursor tests
 * mutate, is in the seed, so the discovered catalog is the same whichever class runs first.
 */
object SnowflakeSharedSchema {
    private val log = KotlinLogging.logger {}

    private val adminSpec: SnowflakeSourceConfigurationSpecification by lazy {
        SnowflakeLiveTestSupport.spec(sessionTimezone = null)
    }

    val database: String
        get() = adminSpec.database

    private val lazyName = lazy {
        val schema = newSchemaName()
        connect(adminSpec).use { conn ->
            log.info { "Creating test schema $database.$schema" }
            execute(conn, "CREATE SCHEMA \"$database\".\"$schema\"")
            executeScript(conn, "seed.sql", mapOf("DB" to database, "SCHEMA" to schema))
        }
        schema
    }

    /** Concurrent test classes block here until the schema is seeded. */
    val name: String by lazyName

    fun dropIfCreated() {
        if (!lazyName.isInitialized()) return
        connect(adminSpec).use { conn ->
            execute(conn, "DROP SCHEMA IF EXISTS \"$database\".\"$name\" CASCADE")
            log.info { "Dropped test schema $database.$name" }
        }
    }
}

/**
 * Registers the schema drop in the root extension store, which JUnit closes once every test in the
 * JVM has run. [AbstractSnowflakeLiveTest] applies this to every live test class.
 */
class SnowflakeSharedSchemaExtension : BeforeAllCallback {
    override fun beforeAll(context: ExtensionContext) {
        context.root.getStore(ExtensionContext.Namespace.GLOBAL).getOrComputeIfAbsent(
            SnowflakeSharedSchema::class.java.name,
        ) {
            DropOnClose
        }
    }

    private object DropOnClose : AutoCloseable {
        override fun close() = SnowflakeSharedSchema.dropIfCreated()
    }
}
