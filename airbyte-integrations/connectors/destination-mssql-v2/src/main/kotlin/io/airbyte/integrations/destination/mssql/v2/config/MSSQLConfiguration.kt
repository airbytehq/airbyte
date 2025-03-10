/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfiguration
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.MSSQLCSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.file.NoopProcessor
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream

data class MSSQLConfiguration(
    val host: String,
    val port: Int,
    val database: String,
    val schema: String,
    val user: String?,
    val password: String?,
    val jdbcUrlParams: String?,
    val sslMethod: EncryptionMethod,
    override val mssqlLoadTypeConfiguration: MSSQLLoadTypeConfiguration,
) :
    DestinationConfiguration(),
    MSSQLLoadTypeConfigurationProvider,
    AzureBlobStorageConfigurationProvider,
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<ByteArrayOutputStream> {
    override val numProcessRecordsWorkers = 1
    override val numProcessBatchWorkers: Int = 1
    override val processEmptyFiles: Boolean = true
    override val recordBatchSizeBytes = ObjectStorageUploadConfiguration.DEFAULT_PART_SIZE_BYTES
    override val objectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = "blob",
            pathPattern = "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${EPOCH}/",
            fileNamePattern = "{part_number}{format_extension}",
        )
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration =
        MSSQLCSVFormatConfiguration(
            validateValuesPreLoad =
                mssqlLoadTypeConfiguration.loadTypeConfiguration is BulkLoadConfiguration &&
                    mssqlLoadTypeConfiguration.loadTypeConfiguration.validateValuesPreLoad == true
        )
    override val objectStorageCompressionConfiguration:
        ObjectStorageCompressionConfiguration<ByteArrayOutputStream> =
        ObjectStorageCompressionConfiguration(NoopProcessor)
    override val azureBlobStorageConfiguration: AzureBlobStorageConfiguration =
        if (mssqlLoadTypeConfiguration.loadTypeConfiguration is BulkLoadConfiguration)
            AzureBlobStorageConfiguration(
                accountName = mssqlLoadTypeConfiguration.loadTypeConfiguration.accountName,
                containerName = mssqlLoadTypeConfiguration.loadTypeConfiguration.containerName,
                sharedAccessSignature =
                    mssqlLoadTypeConfiguration.loadTypeConfiguration.sharedAccessSignature,
            )
        else
        // TODO: Pull this into a separate config and make a custom condition
        throw IllegalStateException(
                "Azure Blob Storage configuration is only available for Bulk Load"
            )
}

@Singleton
class MSSQLConfigurationFactory(private val featureFlags: Set<FeatureFlag>) :
    DestinationConfigurationFactory<MSSQLSpecification, MSSQLConfiguration> {

    constructor() : this(emptySet())

    override fun makeWithoutExceptionHandling(pojo: MSSQLSpecification): MSSQLConfiguration {
        if (
            pojo.sslMethod is Unencrypted &&
                featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
        ) {
            throw ConfigErrorException("Connection from Airbyte Cloud requires SSL encryption")
        }
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
            sslMethod = spec.sslMethod,
            mssqlLoadTypeConfiguration = spec.toLoadConfiguration()
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
