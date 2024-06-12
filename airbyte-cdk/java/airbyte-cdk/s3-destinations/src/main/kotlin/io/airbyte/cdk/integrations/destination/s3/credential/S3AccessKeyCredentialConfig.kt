/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.credential

import com.amazonaws.auth.AWSCredentials
import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials

class S3AccessKeyCredentialConfig(val accessKeyId: String?, val secretAccessKey: String?) :
    S3CredentialConfig {
    override val credentialType: S3CredentialType
        get() = S3CredentialType.ACCESS_KEY

    override val s3CredentialsProvider: AWSCredentialsProvider
        get() {
            val awsCreds: AWSCredentials = BasicAWSCredentials(accessKeyId, secretAccessKey)
            return AWSStaticCredentialsProvider(awsCreds)
        }
}
