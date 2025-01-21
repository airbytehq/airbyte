/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.iceberg.parquet.CatalogType
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogSpecification
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogSpecifications
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Iceberg V2 Destination Specification")
class S3DataLakeSpecification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    S3BucketSpecification,
    IcebergCatalogSpecifications {

    @get:JsonSchemaTitle("AWS Access Key ID")
    @get:JsonPropertyDescription(
        "The AWS Access Key ID with permissions for S3 and Glue operations."
    )
    @get:JsonSchemaInject(json = """{"airbyte_secret": true, "always_show": true, "order":0}""")
    override val accessKeyId: String? = null

    @get:JsonSchemaTitle("AWS Secret Access Key")
    @get:JsonPropertyDescription(
        "The AWS Secret Access Key paired with the Access Key ID for AWS authentication."
    )
    @get:JsonSchemaInject(json = """{"airbyte_secret": true, "always_show": true, "order":1}""")
    override val secretAccessKey: String? = null

    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription("The name of the S3 bucket that will host the Iceberg data.")
    @get:JsonSchemaInject(json = """{"always_show": true,"order":2}""")
    override val s3BucketName: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"examples":["us-east-1"], "order":3}""")
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.NO_REGION

    @get:JsonSchemaInject(json = """{"order":4}""") override val s3Endpoint: String? = null

    @get:JsonSchemaInject(
        json =
            """
                {
                    "examples": ["s3://your-bucket/path/to/store/files/in"],
                    "always_show": true,
                    "order":5
                }
            """
    )
    override val warehouseLocation: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"order":6}""")
    override val mainBranchName: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"order":7}""")
    override val catalogType: CatalogType = GlueCatalogSpecification(glueId = "")
}

@Singleton
class S3DataLakeSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP
        )
    override val supportsIncremental = true
}
