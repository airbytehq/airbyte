/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class SnowflakeConfiguration(
    val host: String,
    val role: String,
    val warehouse: String,
    val database: String,
    val schema: String,
    val username: String
) : DestinationConfiguration()

// sealed interface CredentialConfiguration
//
// @JsonSchemaTitle("Key Pair Authentication Configuration")
// @JsonSchemaDescription("Key pair specific configuration details for connecting to Snowflake")
// data class PrivateKeyCredentialConfiguration(
//    @JsonSchemaTitle("Private Key")
//    @JsonPropertyDescription("RSA Private key to use for Snowflake connection. See the <a
// href=\"https://docs.airbyte.com/integrations/destinations/snowflake\">docs</a> for more
// information on how to obtain this key.")
//    val privateKey: String
// ): CredentialConfiguration

@Singleton
class SnowflakeConfigurationFactory :
    DestinationConfigurationFactory<SnowflakeSpecification, SnowflakeConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: SnowflakeSpecification
    ): SnowflakeConfiguration {
        return SnowflakeConfiguration(
            host = pojo.host,
            role = pojo.role,
            warehouse = pojo.warehouse,
            database = pojo.database,
            schema = pojo.schema,
            username = pojo.username
        )
    }
}
