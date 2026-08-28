/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.config

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

/** Typed configuration for the Firebolt destination. */
data class FireboltConfiguration(
    val clientId: String,
    val clientSecret: String,
    val account: String,
    val database: String,
    val engine: String?,
    val host: String?,
    val schema: String,
    val jdbcUrlParams: String?,
    val s3Staging: S3StagingConfiguration?,
) : DestinationConfiguration()

/** Factory for creating FireboltConfiguration from FireboltSpecification. */
@Singleton
class FireboltConfigurationFactory :
    DestinationConfigurationFactory<FireboltSpecification, FireboltConfiguration> {

    override fun makeWithoutExceptionHandling(pojo: FireboltSpecification): FireboltConfiguration {
        return FireboltConfiguration(
            clientId = pojo.clientId,
            clientSecret = pojo.clientSecret,
            account = pojo.account,
            database = pojo.database,
            engine = pojo.engine,
            host = pojo.host,
            schema = pojo.schema,
            jdbcUrlParams = pojo.jdbcUrlParams,
            s3Staging = pojo.s3Staging,
        )
    }
}
