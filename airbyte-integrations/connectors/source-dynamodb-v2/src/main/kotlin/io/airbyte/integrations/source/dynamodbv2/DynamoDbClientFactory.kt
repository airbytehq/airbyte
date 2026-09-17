/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import io.github.oshai.kotlinlogging.KotlinLogging
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.dynamodb.DynamoDbClientBuilder

private val log = KotlinLogging.logger {}

/**
 * Builds a [DynamoDbClient] from a [DynamoDbSourceConfiguration], the same way the legacy connector
 * did: static credentials when an access key pair is configured, otherwise the SDK default
 * credentials provider chain (environment, web identity token, instance profile, ...); region and
 * endpoint override only when configured.
 */
object DynamoDbClientFactory {

    fun create(configuration: DynamoDbSourceConfiguration): DynamoDbClient {
        val credentialsProvider: AwsCredentialsProvider =
            if (configuration.hasStaticCredentials) {
                log.info { "Creating credentials using access key and secret key" }
                StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(
                        configuration.accessKeyId,
                        configuration.secretAccessKey,
                    ),
                )
            } else {
                log.info { "Using role based access" }
                DefaultCredentialsProvider.builder().build()
            }
        val builder: DynamoDbClientBuilder =
            DynamoDbClient.builder().credentialsProvider(credentialsProvider)
        configuration.region?.let { builder.region(it) }
        configuration.endpoint?.let { builder.endpointOverride(it) }
        return builder.build()
    }
}
