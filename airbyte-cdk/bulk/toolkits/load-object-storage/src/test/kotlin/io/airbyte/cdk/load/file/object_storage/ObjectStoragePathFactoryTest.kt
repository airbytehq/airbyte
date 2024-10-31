/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.MockTimeProvider
import io.airbyte.cdk.load.file.TimeProvider
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.zip.GZIPOutputStream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    environments =
        [
            "ObjectStoragePathFactoryTest",
            "MockDestinationCatalog",
        ]
)
class ObjectStoragePathFactoryTest {
    @Inject lateinit var timeProvider: TimeProvider

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    class PathTimeProvider : MockTimeProvider() {
        init {
            val dateTime =
                LocalDateTime.parse(
                    "2020-01-02T03:04:05.6789",
                    DateTimeFormatter.ISO_LOCAL_DATE_TIME
                )
            val epochMilli =
                dateTime.toInstant(ZoneId.of("UTC").rules.getOffset(dateTime)).toEpochMilli()
            setCurrentTime(epochMilli)
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    class MockPathConfigProvider : ObjectStoragePathConfigurationProvider {
        override val objectStoragePathConfiguration: ObjectStoragePathConfiguration =
            ObjectStoragePathConfiguration(
                prefix = "prefix",
                stagingPrefix = "staging/prefix",
                pathSuffixPattern =
                    "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${HOUR}/\${MINUTE}/\${SECOND}/\${MILLISECOND}/\${EPOCH}/",
                fileNamePattern = "{date}-{timestamp}-{part_number}-{sync_id}{format_extension}",
                usesStagingDirectory = true
            )
    }

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    class MockFormatConfigProvider : ObjectStorageFormatConfigurationProvider {
        override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration =
            JsonFormatConfiguration()
    }

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    class MockCompressionConfigProvider :
        ObjectStorageCompressionConfigurationProvider<GZIPOutputStream> {
        override val objectStorageCompressionConfiguration:
            ObjectStorageCompressionConfiguration<GZIPOutputStream> =
            ObjectStorageCompressionConfiguration(compressor = GZIPProcessor)
    }

    @Test
    fun testBasicBehavior(pathFactory: ObjectStoragePathFactory) {
        val epochMilli = timeProvider.currentTimeMillis()
        val stream1 = MockDestinationCatalogFactory.stream1
        val (namespace, name) = stream1.descriptor
        val prefixOnly = "prefix/$namespace/$name/2020/01/02/03/04/05/0678/$epochMilli"
        val fileName = "2020_01_02-1577934245678-173-42.jsonl.gz"
        Assertions.assertEquals(
            "staging/$prefixOnly",
            pathFactory.getStagingDirectory(stream1).toString(),
        )
        Assertions.assertEquals(
            prefixOnly,
            pathFactory.getFinalDirectory(stream1).toString(),
        )
        Assertions.assertEquals(
            "staging/$prefixOnly/$fileName",
            pathFactory.getPathToFile(stream1, 173, true).toString(),
        )
        Assertions.assertEquals(
            "$prefixOnly/$fileName",
            pathFactory.getPathToFile(stream1, 173, false).toString(),
        )
    }
}
