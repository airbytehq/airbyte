/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.ObjectStorageDataDumper
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobStorageClientFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
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
    ): Map<String, String> = getObjectStorageDataDumper(spec, stream).dumpFile()

    private fun getObjectStorageDataDumper(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): ObjectStorageDataDumper {
        val config: AzureBlobStorageConfiguration<*> =
            AzureBlobStorageConfigurationFactory()
                .makeWithoutExceptionHandling(spec as AzureBlobStorageSpecification)
        val pathFactory = ObjectStoragePathFactory.from(config)
        val client = AzureBlobStorageClientFactory(config).make()
        return ObjectStorageDataDumper(
            stream,
            client,
            pathFactory,
            config.objectStorageFormatConfiguration,
            config.objectStorageCompressionConfiguration,
        )
    }
}
