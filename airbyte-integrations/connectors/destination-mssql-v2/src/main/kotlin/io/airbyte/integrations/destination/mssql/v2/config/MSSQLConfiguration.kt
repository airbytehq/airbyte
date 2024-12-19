/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import dagger.Component.Factory
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
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
        return MSSQLConfiguration(
            host = pojo.host,
            port = pojo.port,
            database = pojo.database,
            schema = pojo.schema,
            user = pojo.user,
            password = pojo.password,
            jdbcUrlParams = pojo.jdbcUrlParams,
            rawDataSchema = pojo.rawDataSchema,
            sslMethod = pojo.sslMethod,
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
