/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

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
}

interface GcsConfigurationProvider {
    val gcsClientConfiguration: GcsClientConfiguration
}
