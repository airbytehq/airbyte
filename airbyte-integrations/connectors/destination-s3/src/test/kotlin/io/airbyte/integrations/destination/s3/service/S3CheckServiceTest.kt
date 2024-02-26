/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.service

import com.amazonaws.AmazonServiceException
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.CompleteMultipartUploadResult
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult
import com.amazonaws.services.s3.model.ListObjectsRequest
import com.amazonaws.services.s3.model.ObjectListing
import com.amazonaws.services.s3.model.PartETag
import com.amazonaws.services.s3.model.PutObjectResult
import com.amazonaws.services.s3.model.UploadPartResult
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_CONFIG_PREFIX
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST, "destination"])
@Property(name = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION, value = "check")
class S3CheckServiceTest {
    @Inject
    lateinit var s3CheckService: S3CheckService

    private val amazonS3Client: AmazonS3 = mockk()

    @MockBean
    fun amazonS3Client(): AmazonS3 {
        return amazonS3Client
    }

    @Test
    @Property(name = "$CONNECTOR_CONFIG_PREFIX.s3-bucket-name", value = "test-bucket")
    @Property(name = "$CONNECTOR_CONFIG_PREFIX.s3-bucket-path", value = "/test/path")
    internal fun `test that when all S3 internal checks pass, a successful result is returned`() {
        val uploadResult: InitiateMultipartUploadResult = mockk()
        val uploadPartResult: UploadPartResult = mockk()

        every { uploadResult.uploadId } returns "upload-id"
        every { uploadPartResult.partETag } returns mockk<PartETag>()
        every { amazonS3Client.abortMultipartUpload(any()) } returns Unit
        every { amazonS3Client.completeMultipartUpload(any()) } returns mockk<CompleteMultipartUploadResult>()
        every { amazonS3Client.deleteObject("test-bucket", any()) } returns Unit
        every { amazonS3Client.initiateMultipartUpload(any()) } returns uploadResult
        every { amazonS3Client.listObjects(any(ListObjectsRequest::class)) } returns mockk<ObjectListing>()
        every { amazonS3Client.putObject("test-bucket", any(String::class), any(String::class)) } returns mockk<PutObjectResult>()
        every { amazonS3Client.uploadPart(any()) } returns uploadPartResult

        val result = s3CheckService.check()

        assertTrue(result.isSuccess)
        assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, result.getOrNull()?.connectionStatus?.status)
        verify(exactly = 1) { amazonS3Client.listObjects(any(ListObjectsRequest::class)) }
        verify(exactly = 1) { amazonS3Client.putObject("test-bucket", any(String::class), any(String::class)) }
        verify(exactly = 2) { amazonS3Client.deleteObject("test-bucket", any()) }
        verify(exactly = 1) { amazonS3Client.completeMultipartUpload(any()) }
    }

    @Test
    @Property(name = "$CONNECTOR_CONFIG_PREFIX.s3-bucket-name", value = "test-bucket")
    @Property(name = "$CONNECTOR_CONFIG_PREFIX.s3-bucket-path", value = "/test/path")
    internal fun `test that if an exception occurs while attempting to perform the check operation, a successful result is returned containing the failed status`() {
        val uploadResult: InitiateMultipartUploadResult = mockk()
        val uploadPartResult: UploadPartResult = mockk()
        val e = AmazonServiceException("test")

        every { uploadResult.uploadId } returns "upload-id"
        every { uploadPartResult.partETag } returns mockk<PartETag>()
        every { amazonS3Client.abortMultipartUpload(any()) } returns Unit
        every { amazonS3Client.completeMultipartUpload(any()) } returns mockk<CompleteMultipartUploadResult>()
        every { amazonS3Client.deleteObject("test-bucket", any()) } returns Unit
        every { amazonS3Client.initiateMultipartUpload(any()) } returns uploadResult
        every { amazonS3Client.listObjects(any(ListObjectsRequest::class)) } throws e
        every { amazonS3Client.putObject("test-bucket", any(String::class), any(String::class)) } returns mockk<PutObjectResult>()
        every { amazonS3Client.uploadPart(any()) } returns uploadPartResult

        val result = s3CheckService.check()

        assertTrue(result.isSuccess)
        assertEquals(AirbyteConnectionStatus.Status.FAILED, result.getOrNull()?.connectionStatus?.status)
        assertEquals(
            "Could not connect to the S3 bucket with the provided configuration. \n ${e.message}",
            result.getOrNull()?.connectionStatus?.message,
        )
    }
}
