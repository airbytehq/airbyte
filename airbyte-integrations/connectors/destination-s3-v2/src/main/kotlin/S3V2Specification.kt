/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.object_storage.JsonFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification
import io.airbyte.cdk.load.command.s3.S3PathSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("S3 V2 Destination Spec")
class S3V2Specification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    S3BucketSpecification,
    S3PathSpecification,
    ObjectStorageFormatSpecificationProvider {
    override val accessKeyId: String = ""
    override val secretAccessKey: String = ""
    override val s3BucketName: String = ""
    override val s3BucketPath: String = ""
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.`us-west-1`
    override val format: ObjectStorageFormatSpecification = JsonFormatSpecification()
    override val s3Endpoint: String? = null
    override val s3PathFormat: String? = null
    override val fileNamePattern: String? = null
    override val s3StagingPrefix: String? = null
}

@Singleton
class S3V2SpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
}
