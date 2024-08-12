/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.InitiateMultipartUploadRequest
import com.amazonaws.services.s3.model.InitiateMultipartUploadResult
import com.amazonaws.services.s3.model.UploadPartRequest
import com.amazonaws.services.s3.model.UploadPartResult
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory
import io.airbyte.cdk.integrations.destination.s3.StorageProvider
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.mockito.Mockito.mock

class S3DestinationStrictEncryptTest {
    private var s3: AmazonS3 = mock()
    private var factoryConfig: S3DestinationConfigFactory = mock()

    @BeforeEach
    fun setup() {
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

    /** Test that checks if user is using a connection that is HTTPS only */
    @Test
    fun checksCustomEndpointIsHttpsOnly() {
        val destinationWithHttpsOnlyEndpoint: S3Destination =
            S3DestinationStrictEncrypt(factoryConfig, emptyMap<String, String>())
        val status = destinationWithHttpsOnlyEndpoint.check(emptyObject())
        Assertions.assertEquals(
            AirbyteConnectionStatus.Status.SUCCEEDED,
            status!!.status,
            "custom endpoint did not contain `s3-accesspoint`"
        )
    }

    /**
     * Test that checks if user is using a connection that is deemed insecure since it does not
     * always enforce HTTPS only
     *
     * https://docs.aws.amazon.com/general/latest/gr/s3.html
     */
    @Test
    fun checksCustomEndpointIsNotHttpsOnly() {
        val destinationWithStandardUnsecuredEndpoint: S3Destination =
            S3DestinationStrictEncrypt(
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
                            .withEndpoint("s3.us-west-1.amazonaws.com")
                            .withAccessKeyCredential("fake-accessKeyId", "fake-secretAccessKey")
                            .withS3Client(s3)
                            .get()
                    }
                },
                emptyMap<String, String>()
            )
        val status = destinationWithStandardUnsecuredEndpoint.check(emptyObject())
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
    }
}
