/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.dlq

import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import java.io.ByteArrayOutputStream
import java.io.OutputStream

sealed class ObjectStorageConfig<T : OutputStream>(
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration,
) :
    ObjectStorageCompressionConfigurationProvider<T>,
    ObjectStorageFormatConfigurationProvider,
    ObjectStoragePathConfigurationProvider

class DisabledObjectStorageConfig :
    ObjectStorageConfig<ByteArrayOutputStream>(
        objectStorageCompressionConfiguration =
            ObjectStorageCompressionSpecificationProvider.getNoCompressionConfiguration(),
        objectStorageFormatConfiguration = CSVFormatConfiguration(),
        objectStoragePathConfiguration = ObjectStoragePathConfiguration("disabled/", null, null),
    )

class S3ObjectStorageConfig<T : OutputStream>(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val awsArnRoleConfiguration: AWSArnRoleConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,
    objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    objectStoragePathConfiguration: ObjectStoragePathConfiguration,
) :
    ObjectStorageConfig<T>(
        objectStorageCompressionConfiguration = objectStorageCompressionConfiguration,
        objectStorageFormatConfiguration = objectStorageFormatConfiguration,
        objectStoragePathConfiguration = objectStoragePathConfiguration,
    ),
    AWSAccessKeyConfigurationProvider,
    AWSArnRoleConfigurationProvider,
    S3BucketConfigurationProvider

fun ObjectStorageSpec.toObjectStorageConfig(): ObjectStorageConfig<*> =
    when (this) {
        is DisabledObjectStorageSpec -> DisabledObjectStorageConfig()
        is S3ObjectStorageSpec ->
            S3ObjectStorageConfig(
                awsAccessKeyConfiguration = toAWSAccessKeyConfiguration(),
                awsArnRoleConfiguration = toAWSArnRoleConfiguration(),
                s3BucketConfiguration = toS3BucketConfiguration(),
                objectStorageCompressionConfiguration = toCompressionConfiguration(),
                objectStorageFormatConfiguration = toObjectStorageFormatConfiguration(),
                objectStoragePathConfiguration =
                    ObjectStoragePathConfiguration(
                        prefix = bucketPath,
                        pathPattern = normalizePathFormat(pathFormat),
                        fileNamePattern = fileNameFormat,
                    )
            )
    }

/**
 * Normalize the path format to match how the internals of the object storage toolkit work.
 *
 * - pathPattern requires variables to be `${VAR}` (both $ and Uppercase)
 * - pathPattern doesn't guarantee it is only a path, to avoid path leaking into the filename, we
 * add a trailing '/'.
 */
internal fun normalizePathFormat(format: String?): String? =
    format?.let {
        val pathWithCorrectVars =
            it.replace("""\{\w+}""".toRegex()) { match -> "${'$'}${match.value.uppercase()}" }
        if (pathWithCorrectVars.endsWith('/')) pathWithCorrectVars else "$pathWithCorrectVars/"
    }
