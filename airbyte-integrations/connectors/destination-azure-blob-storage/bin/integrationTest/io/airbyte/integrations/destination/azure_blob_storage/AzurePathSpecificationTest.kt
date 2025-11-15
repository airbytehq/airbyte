/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.mockk.every
import io.mockk.mockk
import java.io.BufferedOutputStream
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AzurePathSpecificationTest {

    @Test
    fun testAzureOutputPath() {
        val azureConfig: AzureBlobStorageConfiguration<BufferedOutputStream> =
            AzureBlobStorageConfiguration(mockk(), mockk(), mockk())

        val objectStoragePathConfigProvider: ObjectStoragePathConfigurationProvider = mockk {
            every { this@mockk.objectStoragePathConfiguration } returns
                azureConfig.objectStoragePathConfiguration
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
                    "namespace9/!_.*')(&\$@=;:+,?-^.",
                    "stream_name7/!_.*')(&\$@=;:+,?-^",
                )
        }

        val pathToFile = objectStoragePathFactory.getPathToFile(stream, 123L)

        Assertions.assertEquals(
            "namespace9/!_.*')(&\$@=;:+,?-__/stream_name7/!_.*')(&\$@=;:+,?-_/2020_01_02_1577934245679_123",
            pathToFile,
        )
    }
}
