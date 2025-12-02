/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.constant

class S3Constants {
    companion object {
        const val S_3_BUCKET_PATH: String = "s3_bucket_path"
        const val FILE_NAME_PATTERN: String = "file_name_pattern"
        const val S_3_PATH_FORMAT: String = "s3_path_format"
        const val S_3_ENDPOINT: String = "s3_endpoint"
        const val ACCESS_KEY_ID: String = "access_key_id"
        const val S_3_ACCESS_KEY_ID: String = "s3_access_key_id"
        const val S_3_SECRET_ACCESS_KEY: String = "s3_secret_access_key"
        const val SECRET_ACCESS_KEY: String = "secret_access_key"
        const val S_3_BUCKET_NAME: String = "s3_bucket_name"
        const val S_3_BUCKET_REGION: String = "s3_bucket_region"
        const val ROLE_ARN: String = "role_arn"

        // r2 requires account_id
        const val ACCOUNT_ID: String = "account_id"
    }
}
