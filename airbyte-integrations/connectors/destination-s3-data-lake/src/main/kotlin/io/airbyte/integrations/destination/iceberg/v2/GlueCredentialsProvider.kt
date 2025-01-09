/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.services.sts.StsClient
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest

const val MODE = "mode"
const val MODE_STATIC_CREDS = "static-creds"
const val MODE_ASSUME_ROLE = "assume-role"

const val ACCESS_KEY_ID = "access-key-id"
const val SECRET_ACCESS_KEY = "secret-access-key"

const val ASSUME_ROLE_EXTERNAL_ID = "external-id"
const val ASSUME_ROLE_ARN = "role-arn"

class GlueCredentialsProvider private constructor(private val credentials: AwsCredentials) :
    AwsCredentialsProvider {
    override fun resolveCredentials(): AwsCredentials {
        return this.credentials
    }

    companion object {
        @JvmStatic
        fun create(properties: Map<String, String>): AwsCredentialsProvider {
            val mode = properties[MODE]
            val accessKey = properties[ACCESS_KEY_ID]
            val secretKey = properties[SECRET_ACCESS_KEY]
            return when (mode) {
                MODE_STATIC_CREDS -> {
                    GlueCredentialsProvider(AwsBasicCredentials.create(accessKey, secretKey))
                }
                MODE_ASSUME_ROLE -> {
                    StsAssumeRoleCredentialsProvider.builder()
                        .stsClient(
                            StsClient.builder()
                                .credentialsProvider(
                                    StaticCredentialsProvider.create(
                                        AwsBasicCredentials.create(accessKey, secretKey)
                                    )
                                )
                                .build()
                        )
                        .refreshRequest(
                            AssumeRoleRequest.builder()
                                .externalId(properties[ASSUME_ROLE_EXTERNAL_ID])
                                .roleArn(properties[ASSUME_ROLE_ARN])
                                .roleSessionName("airbyte-sts-session")
                                .build()
                        )
                        .build()
                }
                else -> {
                    throw IllegalArgumentException("Invalid GlueCredentialsProvider mode: $mode")
                }
            }
        }
    }
}
