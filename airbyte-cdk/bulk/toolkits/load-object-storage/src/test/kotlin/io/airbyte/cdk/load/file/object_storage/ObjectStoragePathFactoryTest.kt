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
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Singleton
import java.io.BufferedOutputStream
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class ObjectStoragePathFactoryTest {
    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    class PathTimeProvider : MockTimeProvider(), TimeProvider {
        init {
            val dateTime =
                LocalDateTime.parse(
                    "2020-01-02T03:04:05.6789",
                    DateTimeFormatter.ISO_LOCAL_DATE_TIME
                )
            val epochMilli =
                dateTime.toInstant(ZoneId.of("UTC").rules.getOffset(dateTime)).toEpochMilli()
            setSyncTime(epochMilli)
            setCurrentTime(epochMilli + 1)
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    @Requires(property = "object-storage-path-factory-test.use-staging", value = "true")
    class MockPathConfigProvider : ObjectStoragePathConfigurationProvider {
        override val objectStoragePathConfiguration: ObjectStoragePathConfiguration =
            ObjectStoragePathConfiguration(
                prefix = "prefix",
                pathPattern =
                    "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${HOUR}/\${MINUTE}/\${SECOND}/\${MILLISECOND}/\${EPOCH}/",
                fileNamePattern =
                    "{date}-{date:yyyy_MM}-{timestamp}-{part_number}-{sync_id}{format_extension}",
            )
    }

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    @Requires(property = "object-storage-path-factory-test.path-without-slash", value = "true")
    class MockPathConfigProviderWithoutSlash : ObjectStoragePathConfigurationProvider {
        override val objectStoragePathConfiguration: ObjectStoragePathConfiguration =
            MockPathConfigProvider()
                .objectStoragePathConfiguration
                .copy(
                    pathPattern =
                        "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${HOUR}/\${MINUTE}/\${SECOND}/\${MILLISECOND}/\${EPOCH}_"
                )
    }

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    @Requires(property = "object-storage-path-factory-test.use-staging", value = "false")
    class MockPathConfigProviderWithoutStaging : ObjectStoragePathConfigurationProvider {
        override val objectStoragePathConfiguration: ObjectStoragePathConfiguration =
            MockPathConfigProvider().objectStoragePathConfiguration
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
        ObjectStorageCompressionConfigurationProvider<BufferedOutputStream> {
        override val objectStorageCompressionConfiguration:
            ObjectStorageCompressionConfiguration<BufferedOutputStream> =
            ObjectStorageCompressionConfiguration(compressor = GZIPProcessor)
    }

    @Nested
    @MicronautTest(
        environments =
            [
                "ObjectStoragePathFactoryTest",
                "MockDestinationCatalog",
            ],
    )
    @Property(name = "object-storage-path-factory-test.use-staging", value = "false")
    inner class ObjectStoragePathFactoryTestWithoutStaging {
        @Test
        fun testBasicBehavior(pathFactory: ObjectStoragePathFactory, timeProvider: TimeProvider) {
            val syncTime = timeProvider.syncTimeMillis()
            val wallTime = timeProvider.currentTimeMillis()
            val stream1 = MockDestinationCatalogFactory.stream1
            val (namespace, name) = stream1.descriptor
            val prefixOnly = "prefix/$namespace/$name/2020/01/02/03/04/05/0678/$syncTime/"
            val fileName = "2020_01_02-2020_01-$wallTime-173-42.jsonl.gz"
            Assertions.assertEquals(
                prefixOnly,
                pathFactory.getFinalDirectory(stream1),
            )
            Assertions.assertEquals(
                "$prefixOnly$fileName",
                pathFactory.getPathToFile(stream1, 173),
            )
        }
    }

    @Nested
    @MicronautTest(
        environments =
            [
                "ObjectStoragePathFactoryTest",
                "MockDestinationCatalog",
            ],
    )
    @Property(name = "object-storage-path-factory-test.path-without-slash", value = "true")
    inner class ObjectStoragePathFactoryTestNoTrailingPathSlash {
        @Test
        fun testPathDoesNotHaveTrailingSlash(
            pathFactory: ObjectStoragePathFactory,
            timeProvider: TimeProvider
        ) {
            val syncTime = timeProvider.syncTimeMillis()
            val wallTime = timeProvider.currentTimeMillis()
            val stream1 = MockDestinationCatalogFactory.stream1
            val (namespace, name) = stream1.descriptor
            val prefixOnly = "prefix/$namespace/$name/2020/01/02/03/04/05/0678/${syncTime}_"
            val fileName = "2020_01_02-2020_01-$wallTime-173-42.jsonl.gz"
            Assertions.assertEquals(
                prefixOnly,
                pathFactory.getFinalDirectory(stream1),
            )
            Assertions.assertEquals(
                "$prefixOnly$fileName",
                pathFactory.getPathToFile(stream1, 173),
            )
        }
    }
}
