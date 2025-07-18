/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.mockk.every
import io.mockk.mockk
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class S3PathSpecificationTest {

    @Test
    fun testS3OutputPath() {
        val pathFormat =
            "\${NAMESPACE}/\${STREAM_NAME}/p_date=\${YEAR}-\${MONTH}-\${DAY}/p_hour=\${HOUR}/"
        val fileNamePattern = "{sync_id}_part_{part_number}{format_extension}"

        val s3V2PathSpecification: S3PathSpecification = mockk {
            every { this@mockk.s3BucketPath } returns "this_is_my_bucket_path"
            every { this@mockk.s3PathFormat } returns pathFormat
            every { this@mockk.fileNamePattern } returns fileNamePattern
            every { this@mockk.toObjectStoragePathConfiguration() } answers { callOriginal() }
        }

        val objectStoragePathConfigProvider: ObjectStoragePathConfigurationProvider = mockk {
            every { this@mockk.objectStoragePathConfiguration } returns
                s3V2PathSpecification.toObjectStoragePathConfiguration()
        }

        val dateTime =
            LocalDateTime.parse(
                "2020-01-02T03:04:05.6789",
                DateTimeFormatter.ISO_LOCAL_DATE_TIME,
            )
        val epochMilli =
            dateTime.toInstant(ZoneId.of("UTC").rules.getOffset(dateTime)).toEpochMilli()

        val timeProvider: TimeProvider = mockk {
            every { this@mockk.syncTimeMillis() } returns epochMilli
            every { this@mockk.currentTimeMillis() } returns (epochMilli + 1)
        }

        val objectStoragePathFactory =
            ObjectStoragePathFactory(objectStoragePathConfigProvider, timeProvider = timeProvider)

        val stream: DestinationStream = mockk {
            every { this@mockk.syncId } returns 444L
            every { this@mockk.mappedDescriptor } returns
                DestinationStream.Descriptor(
                    "namespace9/!_.*')(&\$@=;:+,?-^",
                    "stream_name7/!_.*')(&\$@=;:+,?-^",
                )
        }

        val pathToFile = objectStoragePathFactory.getPathToFile(stream, 123L)

        Assertions.assertEquals(
            "this_is_my_bucket_path/namespace9/!_.*')(&\$@=;:+,?-_/stream_name7/!_.*')(&\$@=;:+,?-_/p_date=2020-01-02/p_hour=03/444_part_123",
            pathToFile,
        )
    }
}
