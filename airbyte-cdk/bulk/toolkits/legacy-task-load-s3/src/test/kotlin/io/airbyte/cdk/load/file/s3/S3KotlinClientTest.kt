/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.s3

import aws.sdk.kotlin.services.s3.model.ListObjectsV2Request
import aws.sdk.kotlin.services.s3.model.NoSuchBucket
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class S3KotlinClientTest {
    @Test
    fun `list wraps missing bucket errors as config errors`() = runBlocking {
        val sdkClient = mockk<aws.sdk.kotlin.services.s3.S3Client>()
        val missingBucket = NoSuchBucket {}

        coEvery { sdkClient.listObjectsV2(any<ListObjectsV2Request>()) } throws missingBucket

        val client =
            S3KotlinClient(sdkClient, S3BucketConfiguration("test-bucket", "us-east-1", null))

        val exception = assertThrows<ConfigErrorException> { client.list("prefix").toList() }

        assertEquals(
            "Object storage bucket does not exist or is not accessible. Verify the bucket name and credentials in the destination configuration.",
            exception.message,
        )
        assertSame(missingBucket, exception.cause)
    }
}
