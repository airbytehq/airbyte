/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.spec

import io.airbyte.cdk.command.SshTunnelConfiguration
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.write.db.DbConstants
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton
import kotlin.time.Duration.Companion.seconds

data class RedshiftV2Configuration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    val username: String,
    val password: String,
    val database: String,
    val schema: String,
    val jdbcUrlParams: String?,
    val s3Config: S3StagingConfiguration?,
    /** Schema for internal/temp tables during sync operations. */
    val internalSchema: String,
    val dropCascade: Boolean,
) : DestinationConfiguration(), SshTunnelConfiguration {

    // These will be set after tunnel is established
    var tunnelHost: String = realHost
        internal set
    var tunnelPort: Int = realPort
        internal set

    val jdbcUrl: String
        get() {
            val baseUrl = "jdbc:redshift://$tunnelHost:$tunnelPort/$database"
            return if (jdbcUrlParams.isNullOrBlank()) {
                baseUrl
            } else {
                "$baseUrl?$jdbcUrlParams"
            }
        }
}

data class S3StagingConfiguration(
    val s3BucketName: String,
    val s3BucketPath: String?,
    val s3BucketRegion: String,
    val accessKeyId: String,
    val secretAccessKey: String,
    val fileNamePattern: String?,
    val purgeStagingData: Boolean,
)

@Singleton
class RedshiftV2ConfigurationFactory :
    DestinationConfigurationFactory<RedshiftV2Specification, RedshiftV2Configuration> {

    override fun makeWithoutExceptionHandling(
        pojo: RedshiftV2Specification
    ): RedshiftV2Configuration {
        val s3Config =
            when (val uploadMethod = pojo.uploadingMethod) {
                is S3StagingSpecification ->
                    S3StagingConfiguration(
                        s3BucketName = uploadMethod.s3BucketName,
                        s3BucketPath = uploadMethod.s3BucketPath,
                        s3BucketRegion = uploadMethod.s3BucketRegion,
                        accessKeyId = uploadMethod.accessKeyId,
                        secretAccessKey = uploadMethod.secretAccessKey,
                        fileNamePattern = uploadMethod.fileNamePattern,
                        purgeStagingData = uploadMethod.purgeStagingData ?: true,
                    )
                is StandardSpecification,
                null -> null
            }

        return RedshiftV2Configuration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = pojo.tunnelMethod ?: SshNoTunnelMethod,
            sshConnectionOptions =
                SshConnectionOptions(
                    sessionHeartbeatInterval = 1.seconds,
                    globalHeartbeatInterval = 2.seconds,
                    idleTimeout = 0.seconds, // No timeout
                ),
            username = pojo.username,
            password = pojo.password,
            database = pojo.database,
            schema = pojo.schema,
            jdbcUrlParams = pojo.jdbcUrlParams,
            s3Config = s3Config,
            internalSchema = DbConstants.DEFAULT_RAW_TABLE_NAMESPACE,
            dropCascade = pojo.dropCascade ?: false,
        )
    }
}
