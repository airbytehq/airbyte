/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import com.amazonaws.ClientConfiguration
import com.amazonaws.auth.AWSCredentials
import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.retry.RetryMode
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.spark.S3Client

/** Mix in to a configuration to add AWS access key and secret key fields as properties. */
interface AWSAccessKeySpecification {
    @get:JsonSchemaTitle("S3 Key ID")
    @get:JsonPropertyDescription(
        "The access key ID to access the S3 bucket. Airbyte requires Read and Write permissions to the given bucket. Read more <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">here</a>."
    )
    @get:JsonProperty("access_key_id")
    @get:JsonSchemaInject(json = """{"examples":["A012345678910EXAMPLE"]}""")
    val accessKeyId: String

    @get:JsonSchemaTitle("S3 Access Key")
    @get:JsonPropertyDescription(
        "The corresponding secret to the access key ID. Read more <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">here</a>"
    )
    @get:JsonProperty("secret_access_key")
    @get:JsonSchemaInject(json = """{"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"]}""")
    val secretAccessKey: String

    fun toAWSCredentialsProvider(): AWSCredentialsProvider {
        val awsCreds: AWSCredentials = BasicAWSCredentials(accessKeyId, secretAccessKey)
        return AWSStaticCredentialsProvider(awsCreds)
    }
}

interface AWSCredentialsProviderSupplier {
    val awsCredentialProvider: AWSCredentialsProvider
}

fun <T> T.createS3Client(): S3Client where
T : AWSCredentialsProviderSupplier,
T : S3BucketConfigurationProvider {
    val amazonS3 =
        AmazonS3ClientBuilder.standard()
            .withCredentials(awsCredentialProvider)
            .withRegion(s3BucketConfiguration.s3BucketRegion.name)
            .withClientConfiguration(ClientConfiguration().withRetryMode(RetryMode.STANDARD))
            .build()
    return S3Client(amazonS3, s3BucketConfiguration.s3BucketName, awsCredentialProvider)
}
