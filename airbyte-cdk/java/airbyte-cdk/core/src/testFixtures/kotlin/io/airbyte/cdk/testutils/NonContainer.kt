/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.testutils

import org.testcontainers.containers.JdbcDatabaseContainer

/**
 * This is used when a source (such as Snowflake) relies on an always-on resource and therefore
 * doesn't need an actual container. compatible
 */
class NonContainer(
    private val username: String?,
    private val password: String?,
    private val jdbcUrl: String?,
    private val driverClassName: String?,
    dockerImageName: String
) : JdbcDatabaseContainer<NonContainer>(dockerImageName) {
    override fun getDriverClassName(): String? {
        return driverClassName
    }

    override fun getJdbcUrl(): String? {
        return jdbcUrl
    }

    override fun getUsername(): String? {
        return username
    }

    override fun getPassword(): String? {
        return password
    }

    override fun getTestQueryString(): String? {
        return "SELECT 1"
    }
}
