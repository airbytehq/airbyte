/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.ObjectStorageDataDumper
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord

class AzureBlobStorageDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> = getObjectStorageDataDumper(spec, stream).dump()

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<String> = getObjectStorageDataDumper(spec, stream).dumpFile()

    private fun getObjectStorageDataDumper(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): ObjectStorageDataDumper {
        //        val config =
        //            S3V2ConfigurationFactory().makeWithoutExceptionHandling(spec as
        // AzureBlobStorageSpecification)
        //        val s3Client = S3ClientFactory.make(config, S3V2TestUtils.assumeRoleCredentials)
        //        val pathFactory = ObjectStoragePathFactory.from(config)
        //        return ObjectStorageDataDumper(
        //            stream,
        //            s3Client,
        //            pathFactory,
        //            config.objectStorageFormatConfiguration,
        //            config.objectStorageCompressionConfiguration,
        //        )
        TODO()
    }
}
