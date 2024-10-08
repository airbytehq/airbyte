/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.JsonOutputFormatSpecification
import io.airbyte.cdk.load.command.OutputFormatSpecification
import io.airbyte.cdk.load.command.OutputFormatSpecificationProvider
import io.airbyte.cdk.load.command.S3BucketRegion
import io.airbyte.cdk.load.command.S3BucketSpecification
import io.airbyte.cdk.load.command.S3PathSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.core.annotation.Order
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("S3 V2 Destination Spec")
class S3V2Specification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    S3BucketSpecification,
    S3PathSpecification,
    OutputFormatSpecificationProvider {
    @Order(0) override val accessKeyId: String = ""
    @Order(1) override val secretAccessKey: String = ""
    @Order(3) override val s3BucketName: String = ""
    @Order(4) override val s3BucketPath: String = ""
    @Order(5) override val s3BucketRegion: S3BucketRegion = S3BucketRegion.`us-west-1`
    @Order(6) override val format: OutputFormatSpecification = JsonOutputFormatSpecification()
    @Order(7) override val s3Endpoint: String? = null
    @Order(8) override val s3PathFormat: String? = null
    @Order(9) override val fileNamePattern: String? = null
}

/** Non-client-facing configuration. */
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
