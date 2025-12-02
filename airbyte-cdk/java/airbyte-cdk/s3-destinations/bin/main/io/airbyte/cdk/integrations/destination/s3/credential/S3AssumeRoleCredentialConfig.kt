/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.credential

import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.auth.STSAssumeRoleSessionCredentialsProvider
import com.amazonaws.regions.Regions
import com.amazonaws.services.securitytoken.AWSSecurityTokenServiceClient
import java.util.concurrent.Executors
import java.util.concurrent.ThreadFactory

private const val AIRBYTE_STS_SESSION_NAME = "airbyte-sts-session"

internal class DaemonThreadFactory : ThreadFactory {
    override fun newThread(runnable: Runnable): Thread {
        val thread = Executors.defaultThreadFactory().newThread(runnable)
        thread.isDaemon = true
        return thread
    }
}

/**
 * The S3AssumeRoleCredentialConfig implementation of the S3CredentialConfig returns an
 * STSAssumeRoleSessionCredentialsProvider. The STSAssumeRoleSessionCredentialsProvider
 * automatically refreshes assumed role credentials on a background thread. The roleArn comes from
 * the spec and the externalId, which is used to protect against confused deputy problems, and also
 * is provided through the orchestrator via an environment variable. As of 5/2024, the externalId is
 * set to the workspaceId.
 *
 * @param roleArn The Amazon Resource Name (ARN) of the role to assume.
 */
class S3AssumeRoleCredentialConfig(private val roleArn: String, environment: Map<String, String>) :
    S3CredentialConfig {
    private val externalId: String = environment.getValue("AWS_ASSUME_ROLE_EXTERNAL_ID")

    override val credentialType: S3CredentialType = S3CredentialType.ASSUME_ROLE

    /**
     * AWSCredentialsProvider implementation that uses the AWS Security Token Service to assume a
     * Role and create temporary, short-lived sessions to use for authentication. This credentials
     * provider uses a background thread to refresh credentials. This background thread can be shut
     * down via the close() method when the credentials provider is no longer used.
     */
    override val s3CredentialsProvider: AWSCredentialsProvider by lazy {
        STSAssumeRoleSessionCredentialsProvider.Builder(roleArn, AIRBYTE_STS_SESSION_NAME)
            .withExternalId(externalId)
            .withStsClient(
                AWSSecurityTokenServiceClient.builder()
                    .withRegion(Regions.DEFAULT_REGION)
                    .withCredentials(getCredentialProvider(environment))
                    .build()
            )
            .withAsyncRefreshExecutor(Executors.newSingleThreadExecutor(DaemonThreadFactory()))
            .build()
    }

    companion object {
        @JvmStatic
        fun getCredentialProvider(environment: Map<String, String>): AWSStaticCredentialsProvider {
            return AWSStaticCredentialsProvider(
                BasicAWSCredentials(
                    environment.getValue("AWS_ACCESS_KEY_ID"),
                    environment.getValue("AWS_SECRET_ACCESS_KEY")
                )
            )
        }
    }
}
