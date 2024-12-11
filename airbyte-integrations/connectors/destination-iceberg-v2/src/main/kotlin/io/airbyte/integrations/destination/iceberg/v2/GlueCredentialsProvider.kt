/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider

class GlueCredentialsProvider private constructor(private val credentials: AwsBasicCredentials) :
    AwsCredentialsProvider {
    override fun resolveCredentials(): AwsCredentials {
        return this.credentials
    }

    companion object {
        @JvmStatic
        fun create(properties: Map<String, String>): GlueCredentialsProvider {
            val accessKey =
                properties["access-key-id"]
                    ?: throw IllegalArgumentException("Missing property: access-key-id")
            val secretKey =
                properties["secret-access-key"]
                    ?: throw IllegalArgumentException("Missing property: secret-access-key")
            return GlueCredentialsProvider(AwsBasicCredentials.create(accessKey, secretKey))
        }
    }
}
