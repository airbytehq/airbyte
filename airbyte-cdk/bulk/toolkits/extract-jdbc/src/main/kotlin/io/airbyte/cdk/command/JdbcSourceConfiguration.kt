/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

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

    /** Ordered set of namespaces (typically, schemas) for the connector to consider. */
    val namespaces: Set<String>

    /** When set, each table is queried individually to check for SELECT privileges. */
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
