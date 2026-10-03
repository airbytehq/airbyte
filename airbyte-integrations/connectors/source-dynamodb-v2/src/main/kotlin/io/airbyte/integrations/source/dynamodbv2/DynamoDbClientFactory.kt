/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import io.github.oshai.kotlinlogging.KotlinLogging
import java.net.URI
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.dynamodb.DynamoDbClientBuilder
import software.amazon.awssdk.services.sts.StsClient
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest

private val log = KotlinLogging.logger {}

/**
 * Builds a [DynamoDbClient] from a [DynamoDbSourceConfiguration].
 *
 * Credentials come from the configuration only: the configured access key (with its session token
 * when it is a temporary credential), optionally exchanged for the temporary credentials of an IAM
 * role through `sts:AssumeRole`. The SDK default credentials chain is never consulted.
 */
object DynamoDbClientFactory {

    /** `RoleSessionName` shown in CloudTrail for the assumed role's activity. */
    const val ROLE_SESSION_NAME = "airbyte-source-dynamodb"

    /**
     * @param stsEndpointOverride test hook: sends the `AssumeRole` call to an emulator instead of
     * the regional STS endpoint.
     */
    fun create(
        configuration: DynamoDbSourceConfiguration,
        stsEndpointOverride: URI? = null,
    ): DynamoDbClient {
        val builder: DynamoDbClientBuilder =
            DynamoDbClient.builder()
                .credentialsProvider(credentialsProvider(configuration, stsEndpointOverride))
                .region(configuration.region)
        configuration.endpoint?.let { builder.endpointOverride(it) }
        return builder.build()
    }

    fun credentialsProvider(
        configuration: DynamoDbSourceConfiguration,
        stsEndpointOverride: URI? = null,
    ): AwsCredentialsProvider {
        val accessKey: AwsCredentials =
            if (configuration.sessionToken != null) {
                AwsSessionCredentials.create(
                    configuration.accessKeyId,
                    configuration.secretAccessKey,
                    configuration.sessionToken,
                )
            } else {
                AwsBasicCredentials.create(
                    configuration.accessKeyId,
                    configuration.secretAccessKey,
                )
            }
        val accessKeyProvider: AwsCredentialsProvider = StaticCredentialsProvider.create(accessKey)
        val roleArn: String = configuration.roleArn ?: return accessKeyProvider
        log.info { "Assuming IAM role $roleArn with the configured access key" }
        val stsBuilder =
            StsClient.builder().region(configuration.region).credentialsProvider(accessKeyProvider)
        stsEndpointOverride?.let { stsBuilder.endpointOverride(it) }
        val request: AssumeRoleRequest.Builder =
            AssumeRoleRequest.builder().roleArn(roleArn).roleSessionName(ROLE_SESSION_NAME)
        configuration.externalId?.let { request.externalId(it) }
        return StsAssumeRoleCredentialsProvider.builder()
            .stsClient(stsBuilder.build())
            .refreshRequest(request.build())
            .build()
    }
}
