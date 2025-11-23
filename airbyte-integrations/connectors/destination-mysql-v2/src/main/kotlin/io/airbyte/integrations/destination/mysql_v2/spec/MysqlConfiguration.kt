package io.airbyte.integrations.destination.mysql_v2.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class MysqlConfiguration(
    val host: String,
    val port: Int,
    val database: String,
    val username: String,
    val password: String,
    val ssl: Boolean,
    val sslMode: SslMode,
    val jdbcUrlParams: String?,
    val batchSize: Int,
) : DestinationConfiguration()

@Singleton
class MysqlConfigurationFactory :
    DestinationConfigurationFactory<MysqlSpecification, MysqlConfiguration> {

    override fun makeWithoutExceptionHandling(pojo: MysqlSpecification): MysqlConfiguration {
        return MysqlConfiguration(
            host = pojo.host,
            port = pojo.port,
            database = pojo.database,
            username = pojo.username,
            password = pojo.password,
            ssl = pojo.ssl,
            sslMode = pojo.sslMode ?: SslMode.PREFERRED,
            jdbcUrlParams = pojo.jdbcUrlParams,
            batchSize = pojo.batchSize,
        )
    }
}
