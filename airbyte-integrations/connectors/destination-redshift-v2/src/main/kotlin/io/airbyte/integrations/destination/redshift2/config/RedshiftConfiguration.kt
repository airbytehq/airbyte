/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.config

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.integrations.destination.redshift2.spec.RedshiftSpecification
import io.airbyte.integrations.destination.redshift2.spec.S3StagingConfig
import jakarta.inject.Singleton

/**
 * Typed configuration for Redshift destination.
 * Provides computed properties for JDBC URL and S3 staging configuration.
 */
data class RedshiftConfiguration(
    val host: String,
    val port: Int,
    val database: String,
    val schema: String,
    val username: String,
    val password: String,
    val jdbcUrlParams: String?,
    val uploadingMethod: S3StagingConfig?
) : DestinationConfiguration() {
    
    /** Computed JDBC URL for Redshift connection. */
    val jdbcUrl: String
        get() {
            val baseUrl = "jdbc:redshift://$host:$port/$database"
            return if (jdbcUrlParams.isNullOrBlank()) {
                baseUrl
            } else {
                "$baseUrl?$jdbcUrlParams"
            }
        }
    
    /** Whether S3 staging is configured. */
    val hasS3Staging: Boolean
        get() = uploadingMethod != null
    
    /** S3 staging configuration accessors. */
    val s3BucketName: String?
        get() = uploadingMethod?.s3BucketName
    
    val s3BucketPath: String?
        get() = uploadingMethod?.s3BucketPath
    
    val s3BucketRegion: String?
        get() = uploadingMethod?.s3BucketRegion
    
    val s3AccessKeyId: String?
        get() = uploadingMethod?.accessKeyId
    
    val s3SecretAccessKey: String?
        get() = uploadingMethod?.secretAccessKey
    
    val purgeStagingData: Boolean
        get() = uploadingMethod?.purgeStagingData ?: true
}

/**
 * Factory for creating RedshiftConfiguration from RedshiftSpecification.
 */
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
            uploadingMethod = pojo.uploadingMethod
        )
    }
}
