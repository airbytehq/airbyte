/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.spec

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.table.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton
import software.amazon.awssdk.regions.Region

data class RedshiftV2Configuration(
    val host: String,
    val port: Int,
    val tunnelMethod: SshTunnelMethodConfiguration,
    val username: String,
    val password: String,
    val database: String,
    val schema: String,
    val jdbcUrlParams: String?,
    val s3Config: S3StagingConfiguration,
    /** Schema for internal/temp tables during sync operations. */
    val internalSchema: String,
    val dropCascade: Boolean,
) : DestinationConfiguration() {

    /** Constructs JDBC URL from host:port endpoint and database. */
    fun buildJdbcUrl(endpoint: String): String {
        val queryString =
            if (jdbcUrlParams.isNullOrBlank()) {
                ""
            } else {
                "?$jdbcUrlParams"
            }
        return "jdbc:redshift://$endpoint/$database$queryString"
    }
}

data class S3StagingConfiguration(
    val s3BucketName: String,
    val s3BucketPath: String?,
    val s3BucketRegion: Region,
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
        if (pojo.uploadingMethod == null) {
            throw ConfigErrorException("Expected nonnull uploading method config")
        }
        val uploadMethod = pojo.uploadingMethod as S3StagingSpecification
        val s3Config =
            S3StagingConfiguration(
                s3BucketName = uploadMethod.s3BucketName,
                s3BucketPath = uploadMethod.s3BucketPath,
                s3BucketRegion = Region.of(uploadMethod.s3BucketRegion.ifEmpty { "us-east-1" }),
                accessKeyId = uploadMethod.accessKeyId,
                secretAccessKey = uploadMethod.secretAccessKey,
                fileNamePattern = uploadMethod.fileNamePattern,
                purgeStagingData = uploadMethod.purgeStagingData ?: true,
            )

        return RedshiftV2Configuration(
            host = pojo.host,
            port = pojo.port,
            tunnelMethod = pojo.tunnelMethod ?: SshNoTunnelMethod,
            username = pojo.username,
            password = pojo.password,
            database = pojo.database,
            schema = pojo.schema,
            jdbcUrlParams = pojo.jdbcUrlParams,
            s3Config = s3Config,
            internalSchema = pojo.internalTableSchema ?: DEFAULT_AIRBYTE_INTERNAL_NAMESPACE,
            dropCascade = pojo.dropCascade ?: false,
        )
    }
}
