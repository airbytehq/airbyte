/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.config

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton

/** Typed configuration for Redshift destination. */
data class RedshiftConfiguration(
    val host: String,
    val port: Int,
    val database: String,
    val schema: String,
    val username: String,
    val password: String,
    val jdbcUrlParams: String?,
    val uploadingMethod: S3StagingConfiguration?,
    val tunnelMethod: SshTunnelMethodConfiguration?,
    val dropCascade: Boolean,
) : DestinationConfiguration()

/** Factory for creating RedshiftConfiguration from RedshiftSpecification. */
@Singleton
class RedshiftConfigurationFactory :
    DestinationConfigurationFactory<RedshiftSpecification, RedshiftConfiguration> {

    override fun makeWithoutExceptionHandling(pojo: RedshiftSpecification): RedshiftConfiguration {
        return RedshiftConfiguration(
            host = pojo.host,
            port = pojo.port,
            database = pojo.database,
            schema = pojo.schema,
            username = pojo.username,
            password = pojo.password,
            jdbcUrlParams = pojo.jdbcUrlParams,
            uploadingMethod = pojo.uploadingMethod,
            tunnelMethod = pojo.getTunnelMethodValue(),
            dropCascade = pojo.dropCascade ?: false,
        )
    }
}
