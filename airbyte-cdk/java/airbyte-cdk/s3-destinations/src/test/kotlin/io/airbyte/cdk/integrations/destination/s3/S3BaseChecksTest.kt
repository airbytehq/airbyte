/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.ListObjectsRequest
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.attemptS3WriteAndDelete
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito

class S3BaseChecksTest {
    private lateinit var s3Client: AmazonS3

    @BeforeEach
    fun setup() {
        s3Client = Mockito.mock(AmazonS3::class.java)
        Mockito.`when`(
                s3Client.doesObjectExist(ArgumentMatchers.anyString(), ArgumentMatchers.eq(""))
            )
            .thenThrow(IllegalArgumentException("Object path must not be empty"))
        Mockito.`when`(
                s3Client.putObject(
                    ArgumentMatchers.anyString(),
                    ArgumentMatchers.eq(""),
                    ArgumentMatchers.anyString()
                )
            )
            .thenThrow(IllegalArgumentException("Object path must not be empty"))
    }

    @Test
    fun attemptWriteAndDeleteS3Object_should_createSpecificFiles() {
        val config =
            S3DestinationConfig(
                null,
                "test_bucket",
                "test/bucket/path",
                null,
                null,
                null,
                null,
                s3Client!!
            )
        val operations = S3StorageOperations(S3NameTransformer(), s3Client!!, config)
        Mockito.`when`(s3Client!!.doesObjectExist("test_bucket", "test/bucket/path/"))
            .thenReturn(false)

        attemptS3WriteAndDelete(operations, config, "test/bucket/path")

        Mockito.verify(s3Client)
            .putObject(
                ArgumentMatchers.eq("test_bucket"),
                ArgumentMatchers.startsWith("test/bucket/path/_airbyte_connection_test_"),
                ArgumentMatchers.anyString()
            )
        Mockito.verify(s3Client)
            .listObjects(
                ArgumentMatchers.argThat { request: ListObjectsRequest ->
                    "test_bucket" == request.bucketName
                }
            )
        Mockito.verify(s3Client)
            .deleteObject(
                ArgumentMatchers.eq("test_bucket"),
                ArgumentMatchers.startsWith("test/bucket/path/_airbyte_connection_test_")
            )
    }

    @Test
    fun attemptWriteAndDeleteS3Object_should_skipDirectoryCreateIfRootPath() {
        val config =
            S3DestinationConfig(null, "test_bucket", "", null, null, null, null, s3Client!!)
        val operations = S3StorageOperations(S3NameTransformer(), s3Client!!, config)

        attemptS3WriteAndDelete(operations, config, "")

        Mockito.verify(s3Client, Mockito.never()).putObject("test_bucket", "", "")
        Mockito.verify(s3Client)
            .putObject(
                ArgumentMatchers.eq("test_bucket"),
                ArgumentMatchers.startsWith("_airbyte_connection_test_"),
                ArgumentMatchers.anyString()
            )
        Mockito.verify(s3Client)
            .listObjects(
                ArgumentMatchers.argThat { request: ListObjectsRequest ->
                    "test_bucket" == request.bucketName
                }
            )
        Mockito.verify(s3Client)
            .deleteObject(
                ArgumentMatchers.eq("test_bucket"),
                ArgumentMatchers.startsWith("_airbyte_connection_test_")
            )
    }

    @Test
    fun attemptWriteAndDeleteS3Object_should_skipDirectoryCreateIfNullPath() {
        val config =
            S3DestinationConfig(null, "test_bucket", null, null, null, null, null, s3Client!!)
        val operations = S3StorageOperations(S3NameTransformer(), s3Client!!, config)

        attemptS3WriteAndDelete(operations, config, null)

        Mockito.verify(s3Client, Mockito.never()).putObject("test_bucket", "", "")
        Mockito.verify(s3Client)
            .putObject(
                ArgumentMatchers.eq("test_bucket"),
                ArgumentMatchers.startsWith("_airbyte_connection_test_"),
                ArgumentMatchers.anyString()
            )
        Mockito.verify(s3Client)
            .listObjects(
                ArgumentMatchers.argThat { request: ListObjectsRequest ->
                    "test_bucket" == request.bucketName
                }
            )
        Mockito.verify(s3Client)
            .deleteObject(
                ArgumentMatchers.eq("test_bucket"),
                ArgumentMatchers.startsWith("_airbyte_connection_test_")
            )
    }
}
