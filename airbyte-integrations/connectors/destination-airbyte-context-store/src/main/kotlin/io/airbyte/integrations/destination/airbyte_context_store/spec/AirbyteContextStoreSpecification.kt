/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.airbyte_context_store.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.iceberg.parquet.CatalogType
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogSpecification
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogSpecifications
import io.airbyte.integrations.destination.s3_data_lake.spec.S3BucketRegion
import io.airbyte.integrations.destination.s3_data_lake.spec.S3BucketSpecification
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeSpecification
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton

const val ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY = "acknowledge_managed_storage"

/**
 * Specification for the fully managed context store.
 *
 * [acknowledgeManagedStorage] is the only property customers see: everything else is supplied by
 * Airbyte at runtime and is removed from the published spec by
 * [AirbyteContextStoreSpecificationExtender].
 */
@Singleton
@Replaces(S3DataLakeSpecification::class)
@JsonSchemaTitle("Airbyte Agents Context Store Specification")
class AirbyteContextStoreSpecification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    S3BucketSpecification,
    IcebergCatalogSpecifications {

    @get:JsonSchemaTitle("Airbyte-managed storage")
    @get:JsonPropertyDescription(
        "Storage for the Airbyte Agents Context Store is fully managed by Airbyte. " +
            "There is nothing to configure: Airbyte provisions the storage location, the catalog " +
            "and the credentials for you, and no storage details are exposed to or accepted from " +
            "this connection. Acknowledge to continue."
    )
    @get:JsonProperty(ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY, required = true)
    @get:JsonSchemaInject(json = """{"default": false, "order": 0}""")
    val acknowledgeManagedStorage: Boolean = false

    override val accessKeyId: String? = null

    override val secretAccessKey: String? = null

    override val s3BucketName: String = ""

    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.NO_REGION

    override val s3Endpoint: String? = null

    override val warehouseLocation: String = ""

    override val mainBranchName: String = "main"

    override val catalogType: CatalogType = GlueCatalogSpecification(glueId = "", databaseName = "")

    @get:JsonProperty("flush_batch_size_mb", required = false)
    val flushBatchSizeMb: Long? = null
}
