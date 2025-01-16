/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class MSSQLConfiguration(
    val host: String,
    val port: Int,
    val database: String,
    val schema: String,
    val user: String?,
    val password: String?,
    val jdbcUrlParams: String?,
    val rawDataSchema: String,
    val sslMethod: EncryptionMethod,
) : DestinationConfiguration()

@Singleton
class MSSQLConfigurationFactory :
    DestinationConfigurationFactory<MSSQLSpecification, MSSQLConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: MSSQLSpecification): MSSQLConfiguration {
        return makeWithOverrides(spec = pojo)
    }

    fun makeWithOverrides(
        spec: MSSQLSpecification,
        overrides: Map<String, String> = emptyMap()
    ): MSSQLConfiguration {
        return MSSQLConfiguration(
            host = overrides.getOrDefault("host", spec.host),
            port = overrides.getOrDefault("port", spec.port.toString()).toInt(),
            database = overrides.getOrDefault("database", spec.database),
            schema = overrides.getOrDefault("schema", spec.schema),
            user = overrides.getOrDefault("user", spec.user),
            password = overrides.getOrDefault("password", spec.password),
            jdbcUrlParams = overrides.getOrDefault("jdbcUrlParams", spec.jdbcUrlParams),
            rawDataSchema = overrides.getOrDefault("rawDataSchema", spec.rawDataSchema),
            sslMethod = spec.sslMethod,
        )
    }
}

@Factory
class MSSQLConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): MSSQLConfiguration {
        return config as MSSQLConfiguration
    }
}
