/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.service

import com.amazonaws.AmazonServiceException
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.*
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import java.util.stream.Stream

@MicronautTest(environments = [Environment.TEST, "destination"])
@Property(name = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION, value = "check")
class S3BaseChecksTest {
    companion object {
        @JvmStatic
        fun getCustomEndpointArguments(): Stream<Arguments> {
            return Stream.of(
                Arguments.arguments("http://not-secure", false),
                Arguments.arguments("https://secured", true),
                Arguments.arguments("", true),
                Arguments.arguments(null, true),
            )
        }
    }

    @Inject
    lateinit var s3BaseChecks: S3BaseChecks

    private val amazonS3Client: AmazonS3 = mockk()

    @MockBean
    fun amazonS3Client(): AmazonS3 {
        return amazonS3Client
    }

    @ParameterizedTest
    @MethodSource("getCustomEndpointArguments")
    internal fun `test that when a custom endpoint is tested, the appropriate response is returned`(
        endpoint: String?,
        expected: Boolean,
    ) {
        assertEquals(expected, s3BaseChecks.testCustomEndpointSecured(endpoint))
    }

    @Test
    internal fun `test that when the IAM user is checked for object permission, the list object method is used`() {
        val bucketName = "bucket-name"
        val listObjectRequest = slot<ListObjectsRequest>()

        every { amazonS3Client.listObjects(any(ListObjectsRequest::class)) } returns mockk<ObjectListing>()

        assertDoesNotThrow {
            s3BaseChecks.testIAMUserHasListObjectPermission(bucketName)
        }

        verify(exactly = 1) { amazonS3Client.listObjects(capture(listObjectRequest)) }
        assertEquals(bucketName, listObjectRequest.captured.bucketName)
    }

    @Test
    internal fun `test that when the IAM user is checked for object permission and is not authorized, an exception is thrown`() {
        val bucketName = "bucket-name"
        val listObjectRequest = slot<ListObjectsRequest>()

        every { amazonS3Client.listObjects(any(ListObjectsRequest::class)) } throws AmazonServiceException("test")

        assertThrows<AmazonServiceException> {
            s3BaseChecks.testIAMUserHasListObjectPermission(bucketName)
        }

        verify(exactly = 1) { amazonS3Client.listObjects(capture(listObjectRequest)) }
        assertEquals(bucketName, listObjectRequest.captured.bucketName)
    }

    @Test
    internal fun `test that when a multipart upload is attempted and is successful, no exception is thrown`() {
        val bucketName = "bucket-name"
        val uploadResult: InitiateMultipartUploadResult = mockk()
        val uploadPartResult: UploadPartResult = mockk()
        val initialMultipartUploadRequest = slot<InitiateMultipartUploadRequest>()

        every { uploadResult.uploadId } returns "upload-id"
        every { uploadPartResult.partETag } returns mockk<PartETag>()
        every { amazonS3Client.abortMultipartUpload(any()) } returns Unit
        every { amazonS3Client.completeMultipartUpload(any()) } returns mockk<CompleteMultipartUploadResult>()
        every { amazonS3Client.deleteObject(bucketName, any()) } returns Unit
        every { amazonS3Client.initiateMultipartUpload(any()) } returns uploadResult
        every { amazonS3Client.uploadPart(any()) } returns uploadPartResult

        assertDoesNotThrow {
            s3BaseChecks.testMultipartUpload(bucketName, "/test/path")
        }

        verify(exactly = 1) { amazonS3Client.initiateMultipartUpload(capture(initialMultipartUploadRequest)) }
        verify(exactly = 1) { amazonS3Client.deleteObject(bucketName, any()) }
        assertEquals(bucketName, initialMultipartUploadRequest.captured.bucketName)
    }

    @Test
    internal fun `test that when a multipart upload is attempted and is unsuccessful, an exception is thrown`() {
        val bucketName = "bucket-name"
        val uploadPartResult: UploadPartResult = mockk()
        val initialMultipartUploadRequest = slot<InitiateMultipartUploadRequest>()

        every { uploadPartResult.partETag } returns mockk<PartETag>()
        every { amazonS3Client.abortMultipartUpload(any()) } returns Unit
        every { amazonS3Client.deleteObject(bucketName, any()) } returns Unit
        every { amazonS3Client.initiateMultipartUpload(any()) } throws AmazonServiceException("test")

        assertThrows<AmazonServiceException> {
            s3BaseChecks.testMultipartUpload(bucketName, "/test/path")
        }

        verify(exactly = 1) { amazonS3Client.initiateMultipartUpload(capture(initialMultipartUploadRequest)) }
        verify(exactly = 1) { amazonS3Client.deleteObject(bucketName, any()) }
        assertEquals(bucketName, initialMultipartUploadRequest.captured.bucketName)
    }

    @Test
    internal fun `test that when a single upload is tested, the put object method on the Amazon client is called`() {
        val bucketName = "bucke-=name"

        every { amazonS3Client.deleteObject(bucketName, any()) } returns Unit
        every { amazonS3Client.putObject(bucketName, any(String::class), any(String::class)) } returns mockk<PutObjectResult>()

        assertDoesNotThrow {
            s3BaseChecks.testSingleUpload(bucketName, "/test/path")
        }

        verify(exactly = 1) { amazonS3Client.putObject(bucketName, any(String::class), any(String::class)) }
        verify(exactly = 1) { amazonS3Client.deleteObject(bucketName, any()) }
    }

    @Test
    internal fun `test that when a single upload is tested and fails, the exception is thrown`() {
        val bucketName = "bucke-=name"

        every { amazonS3Client.deleteObject(bucketName, any()) } returns Unit
        every { amazonS3Client.putObject(bucketName, any(String::class), any(String::class)) } throws AmazonServiceException("test")

        assertThrows<AmazonServiceException> {
            s3BaseChecks.testSingleUpload(bucketName, "/test/path")
        }

        verify(exactly = 1) { amazonS3Client.putObject(bucketName, any(String::class), any(String::class)) }
        verify(exactly = 1) { amazonS3Client.deleteObject(bucketName, any()) }
    }
}
