/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Connection

@Singleton
@Primary
class PostgresSourceJdbcConnectionFactory(config: JdbcSourceConfiguration) :
    JdbcConnectionFactory(config) {
    override fun get(): Connection {
        // Setting autoCommit to false in pg jdbc allows the driver to start returning result before
        // the entire result set is received from the server. This improves performance and memory
        // consumption when fetching large result sets.
        return super.get().also { it.autoCommit = false }
    }
}
