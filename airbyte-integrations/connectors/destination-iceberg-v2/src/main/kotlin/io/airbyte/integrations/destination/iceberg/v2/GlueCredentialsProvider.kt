/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider

const val ACCESS_KEY_ID = "access-key-id"
const val SECRET_ACCESS_KEY = "secret-access-key"

class GlueCredentialsProvider private constructor(private val credentials: AwsBasicCredentials) :
    AwsCredentialsProvider {
    override fun resolveCredentials(): AwsCredentials {
        return this.credentials
    }

    companion object {
        @JvmStatic
        fun create(properties: Map<String, String>): GlueCredentialsProvider {
            val accessKey =
                properties[ACCESS_KEY_ID]
                    ?: throw IllegalArgumentException("Missing property: access-key-id")
            val secretKey =
                properties[SECRET_ACCESS_KEY]
                    ?: throw IllegalArgumentException("Missing property: secret-access-key")
            return GlueCredentialsProvider(AwsBasicCredentials.create(accessKey, secretKey))
        }
    }
}
