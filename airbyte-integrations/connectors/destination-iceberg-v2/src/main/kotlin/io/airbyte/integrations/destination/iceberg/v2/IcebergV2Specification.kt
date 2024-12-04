/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.iceberg.parquet.NessieServerSpecifications
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Iceberg V2 Destination Spec")
class IcebergV2Specification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    S3BucketSpecification,
    NessieServerSpecifications {
    override val accessKeyId: String? = null
    override val secretAccessKey: String? = null
    override val s3BucketName: String = ""
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.`us-west-1`
    override val s3Endpoint: String? = null
    override val serverUri: String = ""
    override val accessToken: String? = null
    override val warehouseLocation: String = ""
    override val mainBranchName: String = ""
}

@Singleton
class IcebergV2SpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP
        )
    override val supportsIncremental = true
}
