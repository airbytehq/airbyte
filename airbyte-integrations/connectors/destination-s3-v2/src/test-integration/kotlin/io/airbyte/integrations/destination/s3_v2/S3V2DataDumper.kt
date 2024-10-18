/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.ObjectStorageDataDumper
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3ClientFactory
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.nio.file.Path

object S3V2DataDumper : DestinationDataDumper {
    override fun dumpRecords(
        configPath: Path,
        stream: DestinationStream
    ): List<OutputRecord> {
        val spec = S3V2TestUtils.getConfig(configPath.toString())
        val config =
            S3V2ConfigurationFactory().makeWithoutExceptionHandling(spec)
        val s3Client = S3ClientFactory.make(config)
        val pathFactory = ObjectStoragePathFactory.from(config)
        return ObjectStorageDataDumper(
                stream,
                s3Client,
                pathFactory,
                config.objectStorageCompressionConfiguration
            )
            .dump()
    }
}
