/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.ObjectStorageDataDumper
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3ClientFactory
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord

class S3V2DataDumper(
    private val assumeRoleAccessKey: String? = null,
    private val assumeRoleSecretKey: String? = null,
    private val assumeRoleExternalId: String? = null,
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        return getObjectStorageDataDumper(spec, stream).dump()
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<String> {
        return getObjectStorageDataDumper(spec, stream).dumpFile()
    }

    private fun getObjectStorageDataDumper(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): ObjectStorageDataDumper {
        val config =
            S3V2ConfigurationFactory().makeWithoutExceptionHandling(spec as S3V2Specification)
        val s3Client =
            S3ClientFactory.make(
                config,
                assumeRoleAccessKey,
                assumeRoleSecretKey,
                assumeRoleExternalId
            )
        val pathFactory = ObjectStoragePathFactory.from(config)
        return ObjectStorageDataDumper(
            stream,
            s3Client,
            pathFactory,
            config.objectStorageFormatConfiguration,
            config.objectStorageCompressionConfiguration,
        )
    }
}
