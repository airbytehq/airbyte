/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.read.LimitState
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

/** Subtype of [SourceConfiguration] for JDBC sources. */
interface JdbcSourceConfiguration : SourceConfiguration {
    /**
     * JDBC URL format string with placeholders for the host and port. These are dynamically
     * assigned by SSH tunnel port forwarding, if applicable.
     */
    val jdbcUrlFmt: String

    /** Properties map (with username, password, etc.) passed along to the JDBC driver. */
    val jdbcProperties: Map<String, String>

    /** Ordered set of schemas for the connector to consider. */
    val schemas: Set<String>

    /** How many rows to query in the first batch. */
    val initialLimit: LimitState
        get() = LimitState.minimum

    val checkPrivileges: Boolean
        get() = true

    /**
     * Micronaut factory which glues [ConfigurationJsonObjectSupplier] and
     * [SourceConfigurationFactory] together to produce a [JdbcSourceConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationJsonObjectBase> jdbcSourceConfig(
            pojoSupplier: ConfigurationJsonObjectSupplier<I>,
            factory: SourceConfigurationFactory<I, out JdbcSourceConfiguration>,
        ): JdbcSourceConfiguration = factory.make(pojoSupplier.get())
    }
}
