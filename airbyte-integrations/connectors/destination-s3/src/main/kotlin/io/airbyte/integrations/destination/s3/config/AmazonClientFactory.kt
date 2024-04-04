/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config

import com.amazonaws.ClientConfiguration
import com.amazonaws.Protocol
import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.client.builder.AwsClientBuilder
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import io.micronaut.core.util.StringUtils
import jakarta.inject.Singleton

@Factory
class AmazonClientFactory {
    @Singleton
    @Requires(notEnv = [Environment.TEST])
    fun awsCredentialsProvider(configuration: S3ConnectorConfiguration): AWSCredentialsProvider {
        return AWSStaticCredentialsProvider(BasicAWSCredentials(configuration.accessKeyId, configuration.secretAccessKey))
    }

    @Singleton
    @Requires(notEnv = [Environment.TEST])
    fun amazonS3Client(
        configuration: S3ConnectorConfiguration,
        awsCredentialsProvider: AWSCredentialsProvider,
    ): AmazonS3 {
        if (StringUtils.isEmpty(configuration.s3Endpoint)) {
            return AmazonS3ClientBuilder.standard()
                .withCredentials(awsCredentialsProvider)
                .withRegion(configuration.s3BucketRegion)
                .build()
        }

        val clientConfiguration = ClientConfiguration().withProtocol(Protocol.HTTPS)
        clientConfiguration.signerOverride = "AWSS3V4SignerType"

        return AmazonS3ClientBuilder.standard()
            .withEndpointConfiguration(AwsClientBuilder.EndpointConfiguration(configuration.s3Endpoint, configuration.s3BucketRegion))
            .withPathStyleAccessEnabled(true)
            .withClientConfiguration(clientConfiguration)
            .withCredentials(awsCredentialsProvider)
            .build()
    }
}
