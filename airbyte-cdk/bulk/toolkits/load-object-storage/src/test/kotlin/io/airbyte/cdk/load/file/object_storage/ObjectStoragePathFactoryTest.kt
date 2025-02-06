/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.data.StringType
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
                stagingPrefix = "staging/prefix",
                pathSuffixPattern =
                    "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${HOUR}/\${MINUTE}/\${SECOND}/\${MILLISECOND}/\${EPOCH}/",
                fileNamePattern =
                    "{date}-{date:yyyy_MM}-{timestamp}-{part_number}-{sync_id}{format_extension}",
                usesStagingDirectory = true
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
                    pathSuffixPattern =
                        "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${HOUR}/\${MINUTE}/\${SECOND}/\${MILLISECOND}/\${EPOCH}_"
                )
    }

    @Singleton
    @Primary
    @Requires(env = ["ObjectStoragePathFactoryTest"])
    @Requires(property = "object-storage-path-factory-test.use-staging", value = "false")
    class MockPathConfigProviderWithoutStaging : ObjectStoragePathConfigurationProvider {
        override val objectStoragePathConfiguration: ObjectStoragePathConfiguration =
            MockPathConfigProvider()
                .objectStoragePathConfiguration
                .copy(usesStagingDirectory = false)
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
    @Property(name = "object-storage-path-factory-test.use-staging", value = "true")
    inner class ObjectStoragePathFactoryTestWithStaging {
        @Test
        fun testBasicBehavior(pathFactory: ObjectStoragePathFactory, timeProvider: TimeProvider) {
            val syncTime = timeProvider.syncTimeMillis()
            val wallTime = timeProvider.currentTimeMillis()
            val stream1 = MockDestinationCatalogFactory.stream1
            val (namespace, name) = stream1.descriptor
            val prefixOnly = "prefix/$namespace/$name/2020/01/02/03/04/05/0678/$syncTime/"
            val fileName = "2020_01_02-2020_01-$wallTime-173-42.jsonl.gz"
            Assertions.assertEquals(
                "staging/$prefixOnly",
                pathFactory.getStagingDirectory(stream1).toString(),
            )
            Assertions.assertEquals(
                prefixOnly,
                pathFactory.getFinalDirectory(stream1).toString(),
            )
            Assertions.assertEquals(
                "staging/$prefixOnly$fileName",
                pathFactory.getPathToFile(stream1, 173, true).toString(),
            )
            Assertions.assertEquals(
                "$prefixOnly$fileName",
                pathFactory.getPathToFile(stream1, 173, false).toString(),
            )
        }

        @Test
        fun testPathMatchingPattern(
            pathFactory: ObjectStoragePathFactory,
            timeProvider: TimeProvider
        ) {
            val syncTime = timeProvider.syncTimeMillis()
            val stream1 = MockDestinationCatalogFactory.stream1
            val (namespace, name) = stream1.descriptor
            val expectedToMatch =
                "prefix/$namespace/$name/2020/01/02/03/04/05/0678/$syncTime/2020_01_02-2020_01-1577934245678-173-42.jsonl.gz"
            val match = pathFactory.getPathMatcher(stream1).match(expectedToMatch)
            Assertions.assertTrue(match != null)
            Assertions.assertTrue(match?.partNumber == 173L)
        }

        @Test
        fun testPathMatchingPatternWithEmptyStream(
            pathFactory: ObjectStoragePathFactory,
            timeProvider: TimeProvider
        ) {
            val epochMilli = timeProvider.currentTimeMillis()
            val stream1 = MockDestinationCatalogFactory.stream1
            val (_, name) = stream1.descriptor
            val emptyNamespaceStream =
                stream1.copy(descriptor = stream1.descriptor.copy(namespace = null))
            val expectedToMatch =
                "prefix/$name/2020/01/02/03/04/05/0678/$epochMilli/2020_01_02-2020_01-1577934245678-173-42.jsonl.gz"
            val match = pathFactory.getPathMatcher(emptyNamespaceStream).match(expectedToMatch)
            Assertions.assertTrue(match != null)
            Assertions.assertTrue(match?.partNumber == 173L)
        }

        @Test
        fun testSpecialCharacterInStream(
            pathFactory: ObjectStoragePathFactory,
            timeProvider: TimeProvider
        ) {
            val epochMilli = timeProvider.syncTimeMillis()
            val streamWithSpecial =
                DestinationStream(
                    DestinationStream.Descriptor(
                        "namespace",
                        "stream_with:spécial:characters",
                    ),
                    generationId = 0,
                    minimumGenerationId = 0,
                    syncId = 0,
                    schema = StringType,
                    importType = Append
                )
            val expectedPath =
                "prefix/namespace/stream_with:special:characters/2020/01/02/03/04/05/0678/$epochMilli/"
            Assertions.assertEquals(
                expectedPath,
                pathFactory.getFinalDirectory(streamWithSpecial),
            )
        }

        @Test
        fun testLongestConstantPrefix(pathFactory: ObjectStoragePathFactory) {
            val stream1 = MockDestinationCatalogFactory.stream1
            val (namespace, name) = stream1.descriptor
            val prefixOnly = "prefix/$namespace/$name/"
            Assertions.assertEquals(
                prefixOnly,
                pathFactory.getLongestStreamConstantPrefix(stream1, false)
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
                pathFactory.getPathToFile(stream1, 173, false),
            )

            Assertions.assertThrows(UnsupportedOperationException::class.java) {
                pathFactory.getStagingDirectory(stream1)
            }
            Assertions.assertThrows(UnsupportedOperationException::class.java) {
                pathFactory.getPathToFile(stream1, 173, true)
            }
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
                pathFactory.getPathToFile(stream1, 173, false),
            )
        }
    }
}
