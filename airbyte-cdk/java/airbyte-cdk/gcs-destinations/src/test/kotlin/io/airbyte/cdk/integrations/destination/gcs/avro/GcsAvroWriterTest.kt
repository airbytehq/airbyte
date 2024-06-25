/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.avro

import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.ObjectMapper
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.base.DestinationConfig.Companion.initialize
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.avro.UploadAvroFormatConfig
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import java.io.IOException
import java.sql.Timestamp
import java.time.Instant
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class GcsAvroWriterTest {
    @Test
    @Throws(IOException::class)
    fun generatesCorrectObjectPath() {
        initialize(Jsons.deserialize("{}"))

        val writer =
            GcsAvroWriter(
                GcsDestinationConfig(
                    "fake-bucket",
                    "fake-bucketPath",
                    "fake-bucketRegion",
                    GcsHmacKeyCredentialConfig("fake-access-id", "fake-secret"),
                    UploadAvroFormatConfig(ObjectMapper().createObjectNode())
                ),
                Mockito.mock(AmazonS3::class.java, Mockito.RETURNS_DEEP_STUBS),
                ConfiguredAirbyteStream()
                    .withStream(
                        AirbyteStream()
                            .withNamespace("fake-namespace")
                            .withName("fake-stream")
                            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
                    ),
                Timestamp.from(Instant.ofEpochMilli(1234)),
                null
            )

        Assertions.assertEquals(
            "fake-bucketPath/fake-namespace/fake-stream/1970_01_01_1234_0.avro",
            writer.outputPath
        )
    }
}
