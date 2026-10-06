/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.ObjectStorageDataDumper
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord

/** Test data dumper: reads back written objects from GCS for verification. */
object GcsV2DataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        return getObjectStorageDataDumper(spec, stream).dump()
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        return getObjectStorageDataDumper(spec, stream).dumpFile()
    }

    private fun getObjectStorageDataDumper(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): ObjectStorageDataDumper {
        val config =
            GcsV2ConfigurationFactory(DestinationCatalog(listOf(stream)))
                .makeWithoutExceptionHandling(spec as GcsV2Specification)
        val gcsClient = GcsV2ClientFactory.make(config.gcsClientConfiguration)
        val pathFactory = ObjectStoragePathFactory.from(config)
        return ObjectStorageDataDumper(
            stream,
            gcsClient,
            pathFactory,
            config.objectStorageFormatConfiguration,
            config.objectStorageCompressionConfiguration,
        )
    }
}
