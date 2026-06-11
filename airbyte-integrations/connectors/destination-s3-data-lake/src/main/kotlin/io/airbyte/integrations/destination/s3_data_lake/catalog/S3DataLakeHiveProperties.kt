/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.catalog

import io.airbyte.cdk.load.command.iceberg.parquet.HiveCatalogConfiguration
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import org.apache.iceberg.CatalogProperties.URI
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_HIVE
import org.apache.iceberg.aws.AwsClientProperties
import org.apache.iceberg.aws.s3.S3FileIOProperties

/**
 * Builds the Iceberg catalog properties for a Hive Metastore catalog.
 *
 * Kept in its own file (rather than inside the upstream [S3DataLakeUtil]) to minimize merge
 * conflicts when syncing from airbytehq/airbyte — the only change required in [S3DataLakeUtil] is a
 * single `when` branch that delegates here.
 *
 * Mirrors the destination-iceberg connector's HiveCatalogConfig: the Hive Metastore thrift URI is
 * passed via [URI], table data lives on S3 via Iceberg's S3FileIO (configured by [s3Properties],
 * which already carries FILE_IO_IMPL, warehouse location, path-style access and the optional
 * endpoint), and S3 credentials are added when present.
 */
fun buildHiveProperties(
    config: S3DataLakeConfiguration,
    catalogConfig: HiveCatalogConfiguration,
    s3Properties: Map<String, String>,
): Map<String, String> {
    require(catalogConfig.hiveThriftUri.startsWith("thrift://")) {
        "hive_thrift_uri must start with 'thrift://' (got '${catalogConfig.hiveThriftUri}')"
    }

    val hiveProperties = buildMap {
        put(CatalogUtil.ICEBERG_CATALOG_TYPE, ICEBERG_CATALOG_TYPE_HIVE)
        put(URI, catalogConfig.hiveThriftUri)

        // Region for the S3FileIO client. Without it the AWS SDK v2 falls through the default
        // region provider chain and fails ("Unable to load region from any of the providers"),
        // since there's no AWS_REGION env var / instance profile in the connector pod. The Glue and
        // REST catalog paths set CLIENT_REGION for the same reason.
        config.s3BucketConfiguration.s3BucketRegion?.let {
            put(AwsClientProperties.CLIENT_REGION, it)
        }

        // S3FileIO credentials for reading/writing data files. Optional: fall back to the default
        // AWS credentials provider chain (e.g. instance profiles) when not explicitly provided.
        config.awsAccessKeyConfiguration.accessKeyId?.let {
            put(S3FileIOProperties.ACCESS_KEY_ID, it)
        }
        config.awsAccessKeyConfiguration.secretAccessKey?.let {
            put(S3FileIOProperties.SECRET_ACCESS_KEY, it)
        }
    }

    // S3-compatible store (Alibaba OSS) compatibility, mirroring destination-iceberg's S3 settings.
    // These intentionally override the toolkit's buildS3Properties defaults, so they are applied
    // LAST (right-most map wins in Map.plus):
    //  - PATH_STYLE_ACCESS=false: OSS only accepts virtual-hosted-style requests and 403s on
    //    path-style ("Please use virtual hosted style to access"); buildS3Properties hardcodes true.
    //  - CHECKSUM_ENABLED=false: OSS doesn't support the AWS SDK v2 flexible-checksum / chunked
    //    trailing checksum, which otherwise breaks PutObject against S3-compatible stores.
    val ossCompatibility =
        mapOf(
            S3FileIOProperties.PATH_STYLE_ACCESS to "false",
            S3FileIOProperties.CHECKSUM_ENABLED to "false",
        )

    return hiveProperties + s3Properties + ossCompatibility
}
