/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.*
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.attemptS3WriteAndDelete
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.s3.StorageProvider
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentCaptor
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.mockito.Mockito.mock

class S3DestinationTest {
    private var s3: AmazonS3 = mock()
    private var config: S3DestinationConfig? = null
    private var factoryConfig: S3DestinationConfigFactory = mock()

    @BeforeEach
    fun setup() {
        s3 = Mockito.mock(AmazonS3::class.java)
        val uploadResult = Mockito.mock(InitiateMultipartUploadResult::class.java)
        val uploadPartResult = Mockito.mock(UploadPartResult::class.java)
        Mockito.`when`(s3.uploadPart(ArgumentMatchers.any(UploadPartRequest::class.java)))
            .thenReturn(uploadPartResult)
        Mockito.`when`(
                s3.initiateMultipartUpload(
                    ArgumentMatchers.any(InitiateMultipartUploadRequest::class.java)
                )
            )
            .thenReturn(uploadResult)

        config =
            S3DestinationConfig.create("fake-bucket", "fake-bucketPath", "fake-region")
                .withEndpoint("fake-endpoint")
                .withAccessKeyCredential("fake-accessKeyId", "fake-secretAccessKey")
                .withS3Client(s3)
                .get()

        factoryConfig =
            object : S3DestinationConfigFactory() {
                override fun getS3DestinationConfig(
                    config: JsonNode,
                    storageProvider: StorageProvider,
                    environment: Map<String, String>
                ): S3DestinationConfig {
                    return S3DestinationConfig.create(
                            "fake-bucket",
                            "fake-bucketPath",
                            "fake-region"
                        )
                        .withEndpoint("https://s3.example.com")
                        .withAccessKeyCredential("fake-accessKeyId", "fake-secretAccessKey")
                        .withS3Client(s3)
                        .get()
                }
            }
    }

    @Test
    /** Test that check will fail if IAM user does not have listObjects permission */
    fun checksS3WithoutListObjectPermission() {
        val destinationFail = S3Destination(factoryConfig, emptyMap<String, String>())
        Mockito.doThrow(AmazonS3Exception("Access Denied"))
            .`when`(s3)
            .listObjects(ArgumentMatchers.any(ListObjectsRequest::class.java))
        val status = destinationFail.check(emptyObject())
        Assertions.assertEquals(
            AirbyteConnectionStatus.Status.FAILED,
            status!!.status,
            "Connection check should have failed"
        )
        Assertions.assertTrue(
            status.message.indexOf("Access Denied") > 0,
            "Connection check returned wrong failure message"
        )
    }

    @Test
    /** Test that check will succeed when IAM user has all required permissions */
    fun checksS3WithListObjectPermission() {
        val destinationSuccess = S3Destination(factoryConfig, emptyMap<String, String>())
        val status = destinationSuccess.check(emptyObject())
        Assertions.assertEquals(
            AirbyteConnectionStatus.Status.SUCCEEDED,
            status!!.status,
            "Connection check should have succeeded"
        )
    }

    @Test
    fun createsThenDeletesTestFile() {
        attemptS3WriteAndDelete(
            Mockito.mock(S3StorageOperations::class.java),
            config!!,
            "fake-fileToWriteAndDelete"
        )

        // We want to enforce that putObject happens before deleteObject, so use inOrder.verify()
        val inOrder = Mockito.inOrder(s3)

        val testFileCaptor = ArgumentCaptor.forClass(String::class.java)
        inOrder
            .verify(s3)
            .putObject(
                ArgumentMatchers.eq("fake-bucket"),
                testFileCaptor.capture(),
                ArgumentMatchers.anyString()
            )

        val testFile = testFileCaptor.value
        Assertions.assertTrue(
            testFile.startsWith("fake-fileToWriteAndDelete/_airbyte_connection_test_"),
            "testFile was actually $testFile"
        )

        inOrder.verify(s3).listObjects(ArgumentMatchers.any(ListObjectsRequest::class.java))
        inOrder.verify(s3).deleteObject("fake-bucket", testFile)

        Mockito.verifyNoMoreInteractions(s3)
    }
}
