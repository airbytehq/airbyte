/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import io.airbyte.cdk.load.command.s3.S3BucketConfiguration

data class GcsClientConfiguration(
    val gcsBucketName: String,
    val path: String,
    val credential: GcsAuthConfiguration,
    val region: GcsRegion?,
) {
    constructor(
        commonSpecification: GcsCommonSpecification,
        regionSpecification: GcsRegion,
    ) : this(
        commonSpecification.gcsBucketName,
        commonSpecification.path,
        commonSpecification.credential.toGcsAuthConfiguration(),
        regionSpecification,
    )

    fun s3BucketConfiguration() =
        S3BucketConfiguration(
            gcsBucketName,
            region?.region,
            GOOGLE_STORAGE_ENDPOINT,
        )
}

interface GcsClientConfigurationProvider {
    val gcsClientConfiguration: GcsClientConfiguration
}
