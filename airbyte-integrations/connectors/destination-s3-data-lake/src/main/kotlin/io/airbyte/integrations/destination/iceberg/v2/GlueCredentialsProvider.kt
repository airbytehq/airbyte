/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.github.oshai.kotlinlogging.KotlinLogging
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.sts.StsClient
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest

const val ACCESS_KEY_ID = "access-key-id"
const val SECRET_ACCESS_KEY = "secret-access-key"

const val ASSUME_ROLE_ACCESS_KEY_ID = "assume-role-access-key-id"
const val ASSUME_ROLE_SECRET_ACCESS_KEY = "assume-role-secret-access-key"
const val ASDF_EXTERNAL_ID = "external-id"
const val ROLE_ARN = "role-arn"

private val logger = KotlinLogging.logger {}
class GlueCredentialsProvider private constructor(private val credentials: AwsCredentials) :
    AwsCredentialsProvider {
    override fun resolveCredentials(): AwsCredentials {
        return this.credentials
    }

    companion object {
        @JvmStatic
        fun create(properties: Map<String, String>): AwsCredentialsProvider {
            val accessKey = properties[ACCESS_KEY_ID]
            val secretKey = properties[SECRET_ACCESS_KEY]
            return if (accessKey != null && secretKey != null) {
                GlueCredentialsProvider(AwsBasicCredentials.create(accessKey, secretKey))
            } else {
                val assumeRoleAccessKey = properties[ASSUME_ROLE_ACCESS_KEY_ID]
                val assumeRoleSecretKey = properties[ASSUME_ROLE_SECRET_ACCESS_KEY]
                StsAssumeRoleCredentialsProvider.builder()
                    .stsClient(
                        StsClient.builder()
                            .credentialsProvider(
                                StaticCredentialsProvider.create(AwsBasicCredentials.create(assumeRoleAccessKey, assumeRoleSecretKey))
                            )
                            // TODO
                            .region(Region.US_EAST_2)
                            .build()
                    )
                    .refreshRequest(
                        AssumeRoleRequest.builder()
                            .externalId(properties[ASDF_EXTERNAL_ID])
                            .roleArn(properties[ROLE_ARN])
                            .roleSessionName("airbyte")
                            .build()
                    ).build()
            }
        }
    }
}
