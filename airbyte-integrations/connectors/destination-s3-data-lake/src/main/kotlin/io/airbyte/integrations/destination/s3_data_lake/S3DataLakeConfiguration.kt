/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.SocketTestConfig
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_NAMESPACE = "airbyte_test_namespace"
const val TEST_TABLE = "airbyte_test_table"

data class S3DataLakeConfiguration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val icebergCatalogConfiguration: IcebergCatalogConfiguration,
    // Now that partitioning is enabled, we can run more than one worker.
    // This will likely not show performance improvements in the cloud without additional
    // resources. In the future, if enterprise or oss users need more flexibility, we can
    // expose this in their configurations.
    override val numProcessRecordsWorkers: Int = 2,

    override val numSockets: Int,
    override val inputSerializationFormat: InputSerializationFormat,
    override val inputBufferByteSizePerSocket: Long,
    override val socketPrefix: String,
    override val socketWaitTimeoutSeconds: Int,
    override val devNullAfterDeserialization: Boolean,
    val skipUpload: Boolean,
    val useGarbagePart: Boolean,
    override val skipJsonOnProto: Boolean,
    override val disableUUID: Boolean,
    override val disableMapper: Boolean,
    override val useCodedInputStream: Boolean = false,
    override val useSnappy: Boolean = false,
    override val runSetup: Boolean = true
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    IcebergCatalogConfigurationProvider,
    S3BucketConfigurationProvider,
    SocketTestConfig

@Singleton
class S3DataLakeConfigurationFactory :
    DestinationConfigurationFactory<S3DataLakeSpecification, S3DataLakeConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: S3DataLakeSpecification
    ): S3DataLakeConfiguration {
        return S3DataLakeConfiguration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            icebergCatalogConfiguration = pojo.toIcebergCatalogConfiguration(),
            numSockets = pojo.numSockets ?: 2,
            numProcessRecordsWorkers = pojo.numInputPartitions ?: 1,
            inputSerializationFormat = pojo.inputSerializationFormat
                ?: DestinationConfiguration.InputSerializationFormat.FLATBUFFERS,
            inputBufferByteSizePerSocket = pojo.inputBufferByteSizePerSocket ?: (16384),
            socketPrefix = pojo.socketPrefix
                ?: "/Users/jschmidt/.sockets/ab_socket_", // "/var/run/sockets/ab_socket_",
            socketWaitTimeoutSeconds = pojo.socketWaitTimeoutSeconds ?: 60,
            devNullAfterDeserialization = pojo.devNullAfterDeserialization ?: false,
            skipUpload = pojo.skipUpload ?: false,
            useGarbagePart = pojo.useGarbagePart ?: false,
            skipJsonOnProto = pojo.skipJsonOnProto ?: true,
            disableUUID = pojo.disableUUID ?: false,
            disableMapper = pojo.disableMapper ?: false,
            useCodedInputStream = pojo.useCodedInputStream ?: true,
            useSnappy = pojo.useSnappy ?: false,
        )
    }
}

@Factory
class S3DataLakeConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): S3DataLakeConfiguration {
        return config as S3DataLakeConfiguration
    }
}
