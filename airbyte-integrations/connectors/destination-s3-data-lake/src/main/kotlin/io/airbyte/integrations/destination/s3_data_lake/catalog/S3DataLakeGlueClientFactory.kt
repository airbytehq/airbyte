/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.catalog

import org.apache.iceberg.aws.AwsClientFactories
import org.apache.iceberg.aws.AwsClientFactory
import org.apache.iceberg.aws.AwsClientProperties
import org.apache.iceberg.aws.AwsProperties
import org.apache.iceberg.aws.HttpClientProperties
import software.amazon.awssdk.awscore.retry.AwsRetryStrategy
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.glue.GlueClient
import software.amazon.awssdk.services.kms.KmsClient
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.S3Client

/**
 * Custom [AwsClientFactory] that increases the maximum retry attempts for the Glue client to handle
 * sustained API throttling during Iceberg metadata operations.
 *
 * The default Iceberg [AwsClientFactory] uses AWS SDK's ADAPTIVE_V2 retry strategy with only 3 max
 * attempts, which is insufficient under heavy Glue API throttling. This factory increases the limit
 * to [MAX_GLUE_RETRY_ATTEMPTS] while preserving the ADAPTIVE_V2 token-bucket-based rate limiting
 * and exponential backoff.
 *
 * Non-Glue client methods delegate to the default Iceberg factory.
 */
class S3DataLakeGlueClientFactory : AwsClientFactory {
    private lateinit var awsClientProperties: AwsClientProperties
    private lateinit var httpClientProperties: HttpClientProperties
    private lateinit var awsProperties: AwsProperties
    private lateinit var catalogProperties: Map<String, String>

    override fun initialize(properties: Map<String, String>) {
        this.catalogProperties = properties
        this.awsClientProperties = AwsClientProperties(properties)
        this.httpClientProperties = HttpClientProperties(properties)
        this.awsProperties = AwsProperties(properties)
    }

    override fun glue(): GlueClient {
        return GlueClient.builder()
            .applyMutation(awsClientProperties::applyClientRegionConfiguration)
            .applyMutation(httpClientProperties::applyHttpClientConfigurations)
            .applyMutation(awsProperties::applyGlueEndpointConfigurations)
            .applyMutation(awsClientProperties::applyClientCredentialConfigurations)
            .overrideConfiguration(
                ClientOverrideConfiguration.builder()
                    .retryStrategy(
                        AwsRetryStrategy.adaptiveRetryStrategy()
                            .toBuilder()
                            .maxAttempts(MAX_GLUE_RETRY_ATTEMPTS)
                            .build()
                    )
                    .build()
            )
            .build()
    }

    private val defaultFactory: AwsClientFactory by lazy {
        val defaultProps = catalogProperties.toMutableMap()
        defaultProps.remove(CLIENT_FACTORY_PROPERTY)
        AwsClientFactories.from(defaultProps)
    }

    override fun s3(): S3Client = defaultFactory.s3()

    override fun s3Async(): S3AsyncClient = defaultFactory.s3Async()

    override fun kms(): KmsClient = defaultFactory.kms()

    override fun dynamo(): DynamoDbClient = defaultFactory.dynamo()

    companion object {
        const val MAX_GLUE_RETRY_ATTEMPTS = 10
        const val CLIENT_FACTORY_PROPERTY = "client.factory"
    }
}
