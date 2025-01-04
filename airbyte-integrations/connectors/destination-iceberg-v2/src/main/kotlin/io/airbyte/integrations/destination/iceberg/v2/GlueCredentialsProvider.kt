/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider

const val ACCESS_KEY_ID = "access-key-id"
const val SECRET_ACCESS_KEY = "secret-access-key"

class GlueCredentialsProvider private constructor(private val credentials: AwsCredentials) :
    AwsCredentialsProvider {
    override fun resolveCredentials(): AwsCredentials {
        return this.credentials
    }

    companion object {
        @JvmStatic
        fun create(properties: Map<String, String>): GlueCredentialsProvider {
            val accessKey = properties[ACCESS_KEY_ID]
            val secretKey = properties[SECRET_ACCESS_KEY]
            val creds =
                if (accessKey != null && secretKey != null) {
                    AwsBasicCredentials.create(accessKey, secretKey)
                } else {
                    DefaultCredentialsProvider.create().resolveCredentials()
                }
            return GlueCredentialsProvider(creds)
        }
    }
}
