/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.file.s3.S3ClientFactory
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.sts.StsClient
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest

const val AWS_CREDENTIALS_MODE = "aws-creds-mode"
const val AWS_CREDENTIALS_MODE_STATIC_CREDS = "aws-creds-static-creds"
const val AWS_CREDENTIALS_MODE_ASSUME_ROLE = "aws-creds-assume-role"

const val ACCESS_KEY_ID = "access-key-id"
const val SECRET_ACCESS_KEY = "secret-access-key"

const val ASSUME_ROLE_EXTERNAL_ID = "external-id"
const val ASSUME_ROLE_ARN = "role-arn"
const val ASSUME_ROLE_REGION = "region"

// This class is required to implement the interface.
// Technically, we don't _need_ to actually return instances of GlueCredentialsProvider,
// i.e. we could just return the delegate directly out of `create`,
// but we might as well?
class GlueCredentialsProvider private constructor(private val delegate: AwsCredentialsProvider) :
    AwsCredentialsProvider by delegate {

    companion object {
        @JvmStatic
        fun create(properties: Map<String, String>): AwsCredentialsProvider {
            val mode = properties[AWS_CREDENTIALS_MODE]
            val accessKey = properties[ACCESS_KEY_ID]
            val secretKey = properties[SECRET_ACCESS_KEY]
            val provider =
                when (mode) {
                    AWS_CREDENTIALS_MODE_STATIC_CREDS -> {
                        if (accessKey != null && secretKey != null) {
                            StaticCredentialsProvider.create(
                                AwsBasicCredentials.create(accessKey, secretKey)
                            )
                        } else {
                            DefaultCredentialsProvider.create()
                        }
                    }
                    AWS_CREDENTIALS_MODE_ASSUME_ROLE -> {
                        StsAssumeRoleCredentialsProvider.builder()
                            .stsClient(
                                StsClient.builder()
                                    .credentialsProvider(
                                        StaticCredentialsProvider.create(
                                            AwsBasicCredentials.create(accessKey, secretKey)
                                        )
                                    )
                                    .region(Region.of(properties[ASSUME_ROLE_REGION]))
                                    .build()
                            )
                            .refreshRequest(
                                AssumeRoleRequest.builder()
                                    .externalId(properties[ASSUME_ROLE_EXTERNAL_ID])
                                    .roleArn(properties[ASSUME_ROLE_ARN])
                                    .roleSessionName(S3ClientFactory.AIRBYTE_STS_SESSION_NAME)
                                    .build()
                            )
                            .build()
                    }
                    else -> {
                        throw IllegalArgumentException(
                            "Invalid GlueCredentialsProvider mode: $mode"
                        )
                    }
                }
            return GlueCredentialsProvider(provider)
        }
    }
}
