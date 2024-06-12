/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.destination.s3.util.S3OutputPathHelper.getOutputPrefix
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class S3OutputPathHelperTest {
    @Test // getOutputPrefix
    fun testGetOutputPrefix() {
        // No namespace
        Assertions.assertEquals(
            "bucket_path/stream_name",
            getOutputPrefix(
                "bucket_path",
                AirbyteStream()
                    .withName("stream_name")
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
            )
        )

        // With namespace
        Assertions.assertEquals(
            "bucket_path/namespace/stream_name",
            getOutputPrefix(
                "bucket_path",
                AirbyteStream()
                    .withNamespace("namespace")
                    .withName("stream_name")
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
            )
        )

        // With empty namespace
        Assertions.assertEquals(
            "bucket_path/stream_name",
            getOutputPrefix(
                "bucket_path",
                AirbyteStream()
                    .withNamespace("")
                    .withName("stream_name")
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
            )
        )

        // With namespace with slash chart in the end
        Assertions.assertEquals(
            "bucket_path/namespace/stream_name",
            getOutputPrefix(
                "bucket_path",
                AirbyteStream()
                    .withNamespace("namespace/")
                    .withName("stream_name")
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
            )
        )

        // With namespace with slash chart in the name
        Assertions.assertEquals(
            "bucket_path/namespace/subfolder/stream_name",
            getOutputPrefix(
                "bucket_path",
                AirbyteStream()
                    .withNamespace("namespace/subfolder/")
                    .withName("stream_name")
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
            )
        )

        // With an AWS Glue crawler
        Assertions.assertEquals(
            "bucket_path/namespace/date=2022-03-15",
            getOutputPrefix(
                "bucket_path",
                AirbyteStream()
                    .withNamespace("namespace")
                    .withName("date=2022-03-15")
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
            )
        )
    }
}
