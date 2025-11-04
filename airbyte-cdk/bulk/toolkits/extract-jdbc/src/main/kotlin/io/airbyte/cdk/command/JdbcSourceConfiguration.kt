/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.ConfigErrorException
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

    /** Optional table filtering configuration for fine-grained table selection. */
    val tableFilters: List<TableFilter>
        get() = emptyList()

    /**
     * Micronaut factory which glues [ConfigurationSpecificationSupplier] and
     * [SourceConfigurationFactory] together to produce a [JdbcSourceConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationSpecification> jdbcSourceConfig(
            pojoSupplier: ConfigurationSpecificationSupplier<I>,
            factory: SourceConfigurationFactory<I, out JdbcSourceConfiguration>,
        ): JdbcSourceConfiguration = factory.make(pojoSupplier.get())
    }

    companion object {
        /**
         * Validates that all schemas referenced in table filters are present in the configured
         * schemas list.
         *
         * @param configuredSchemas The set of schemas configured for the connector
         * @param tableFilters The list of table filters to validate
         * @throws ConfigErrorException if any filter references a schema not in configuredSchemas
         */
        fun validateTableFilters(configuredSchemas: Set<String>, tableFilters: List<TableFilter>) {
            if (tableFilters.isEmpty()) return
            if (configuredSchemas.isEmpty()) return

            val configuredSchemasUpper = configuredSchemas.map { it.uppercase() }.toSet()
            val filterSchemas = tableFilters.map { it.schemaName.uppercase() }.toSet()
            val invalidSchemas = filterSchemas - configuredSchemasUpper

            if (invalidSchemas.isNotEmpty()) {
                throw ConfigErrorException(
                    "Table filters reference schemas not in configured schemas list: $invalidSchemas. " +
                        "Configured schemas: $configuredSchemas"
                )
            }
        }
    }
}
