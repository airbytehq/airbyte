/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.toAirbyteValue
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3ClientFactory
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.toOutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import java.io.InputStream
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import org.junit.jupiter.api.Test

class S3V2WriteTest :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.minimalConfig,
        S3V2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

object S3V2DataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config =
            S3V2ConfigurationFactory().makeWithoutExceptionHandling(spec as S3V2Specification)
        val s3Client = S3ClientFactory.make(config)
        // Note: because we cannot mock wall time in docker, this
        // path code cannot contain time-based macros.
        // TODO: add pattern matching to the path factory.
        val pathFactory = ObjectStoragePathFactory.from(config)
        val prefix = pathFactory.getFinalDirectory(stream).toString()
        return runBlocking {
            withContext(Dispatchers.IO) {
                s3Client
                    .list(prefix)
                    .map { listedObject: S3Object ->
                        s3Client.get(listedObject.key) { objectData: InputStream ->
                            objectData
                                .bufferedReader()
                                .lineSequence()
                                .map { line ->
                                    line
                                        .deserializeToNode()
                                        .toAirbyteValue(stream.schemaWithMeta)
                                        .toOutputRecord()
                                }
                                .toList()
                        }
                    }
                    .toList()
                    .flatten()
            }
        }
    }
}
