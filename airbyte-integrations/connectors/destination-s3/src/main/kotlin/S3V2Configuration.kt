/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.OutputStream

data class S3V2Configuration<T : OutputStream>(
    // Client-facing configuration
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val awsArnRoleConfiguration: AWSArnRoleConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,

    // Internal configuration
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = 1,
    override val estimatedRecordMemoryOverheadRatio: Double = 5.0,
    override val processEmptyFiles: Boolean = true,

    // ObjectLoader-specific configuration
    val numPartWorkers: Int,
    val numUploadWorkers: Int,
    val maxMemoryRatioReservedForParts: Double,
    val objectSizeBytes: Long = 200L * 1024 * 1024,
    val partSizeBytes: Long,

    // TEMPORARY FOR SOCKET TESTS
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
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    AWSArnRoleConfigurationProvider,
    S3BucketConfigurationProvider,
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<T>

@Singleton
class S3V2ConfigurationFactory :
    DestinationConfigurationFactory<S3V2Specification, S3V2Configuration<*>> {
    override fun makeWithoutExceptionHandling(pojo: S3V2Specification): S3V2Configuration<*> {
        return S3V2Configuration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            awsArnRoleConfiguration = pojo.toAWSArnRoleConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            objectStoragePathConfiguration = pojo.toObjectStoragePathConfiguration(),
            objectStorageFormatConfiguration = pojo.toObjectStorageFormatConfiguration(),
            objectStorageCompressionConfiguration = pojo.toCompressionConfiguration(),
            numSockets = pojo.numSockets ?: 1,
            numUploadWorkers = pojo.numPartLoaders ?: 10,
            numPartWorkers = pojo.numPartFormatters ?: pojo.numSockets ?: 1,
            inputSerializationFormat = pojo.inputSerializationFormat
                    ?: DestinationConfiguration.InputSerializationFormat.PROTOBUF,
            partSizeBytes = (pojo.partSizeMb ?: 10) * 1024L * 1024L,
            maxMemoryRatioReservedForParts = pojo.maxMemoryRatioReservedForParts ?: 1.0,
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

@Suppress("UNCHECKED_CAST")
@Factory
class S3V2ConfigurationProvider<T : OutputStream>(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): S3V2Configuration<T> {
        return config as S3V2Configuration<T>
    }
}
