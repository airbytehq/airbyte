/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.credential

import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.auth.STSAssumeRoleSessionCredentialsProvider
import com.amazonaws.regions.Regions
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClient

private const val AIRBYTE_STS_SESSION_NAME = "airbyte-sts-session"

/**
 * The S3AssumeRoleCredentialConfig implementation of the S3CredentialConfig returns an
 * STSAssumeRoleSessionCredentialsProvider. The STSAssumeRoleSessionCredentialsProvider
 * automatically refreshes assumed role credentials on a background thread. To do this, an STS
 * Client is created using the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
 * that are provided by the orchestrator. The roleArn comes from the spec and the externalId, which
 * is used to protect against confused deputy problems, and also is provided through the
 * orchestrator via an environment variable. As of 5/2024, the externalId is set to the workspaceId.
 *
 * @param roleArn The Amazon Resource Name (ARN) of the role to assume.
 */
class S3AssumeRoleCredentialConfig(private val roleArn: String) : S3CredentialConfig {
    // TODO: Verify this env var, I think it might actually be AWS_ASSUME_ROLE_EXTERNAL_ID or
    // something like that.
    private val externalId: String? = System.getenv("AWS_EXTERNAL_ID")

    override val credentialType: S3CredentialType
        get() = S3CredentialType.ASSUME_ROLE

    override val s3CredentialsProvider: AWSCredentialsProvider
        get() {
            /**
             * AWSCredentialsProvider implementation that uses the AWS Security Token Service to
             * assume a Role and create temporary, short-lived sessions to use for authentication.
             * This credentials provider uses a background thread to refresh credentials. This
             * background thread can be shut down via the close() method when the credentials
             * provider is no longer used.
             */
            return STSAssumeRoleSessionCredentialsProvider.Builder(
                    roleArn,
                    AIRBYTE_STS_SESSION_NAME
                )
                .withExternalId(externalId)
                /**
                 * This client is used to make the AssumeRole request. The credentials are
                 * automatically loaded from the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
                 * environment variables set by the orchestrator.
                 */
                .withStsClient(
                    AWSSecurityTokenServiceClient.builder()
                        .withRegion(Regions.DEFAULT_REGION)
                        .build()
                )
                .build()
        }
}
