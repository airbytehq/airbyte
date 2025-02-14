/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.io

import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.s3_data_lake.ACCESS_KEY_ID
import io.airbyte.integrations.destination.s3_data_lake.AWS_CREDENTIALS_MODE
import io.airbyte.integrations.destination.s3_data_lake.AWS_CREDENTIALS_MODE_STATIC_CREDS
import io.airbyte.integrations.destination.s3_data_lake.GlueCredentialsProvider
import io.airbyte.integrations.destination.s3_data_lake.SECRET_ACCESS_KEY
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogProperties.URI
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_GLUE
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_NESSIE
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_REST
import org.apache.iceberg.aws.AwsClientProperties
import org.apache.iceberg.aws.AwsProperties
import org.apache.iceberg.aws.s3.S3FileIO
import org.apache.iceberg.aws.s3.S3FileIOProperties
import org.apache.iceberg.catalog.Catalog
import org.projectnessie.client.NessieConfigConstants

private const val AWS_REGION = "aws.region"

private val logger = KotlinLogging.logger {}

/**
 * Collection of Iceberg related utilities.
 * @param assumeRoleCredentials is a temporary fix to allow us to run the integrations tests. This
 * will be removed when we change all of this to use Micronaut
 */
@Singleton
class GcsDataLakeUtil(private val icebergUtil: IcebergUtil) {
    /**
     * Creates the Iceberg [Catalog] configuration properties from the destination's configuration.
     *
     * @param config The destination's configuration
     * @return The Iceberg [Catalog] configuration properties.
     */
    fun toCatalogProperties(config: GcsDataLakeConfiguration): Map<String, String> {
        val icebergCatalogConfig = config.icebergCatalogConfiguration
        val catalogConfig = icebergCatalogConfig.catalogConfiguration
        val region = config.s3BucketConfiguration.s3BucketRegion.region

        // Build base S3 properties
        val s3Properties = buildS3Properties(config, icebergCatalogConfig)

        return when (catalogConfig) {
            is NessieCatalogConfiguration -> {
                // Set AWS region as system property
                System.setProperty(AWS_REGION, region)
                buildNessieProperties(config, catalogConfig, s3Properties)
            }
            is GlueCatalogConfiguration ->
                buildGlueProperties(config, catalogConfig, icebergCatalogConfig, region)
            is RestCatalogConfiguration -> {
                //                System.setProperty(AWS_REGION, region)
                buildRestProperties(config, catalogConfig, s3Properties, region)
            }
            else ->
                throw IllegalArgumentException(
                    "Unsupported catalog type: ${catalogConfig::class.java.name}"
                )
        }
    }

    // TODO this + nessie probably belong in base CDK toolkit
    private fun buildRestProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig: RestCatalogConfiguration,
        s3Properties: Map<String, String>,
        region: String
    ): Map<String, String> {
        val awsAccessKeyId =
            requireNotNull(config.awsAccessKeyConfiguration.accessKeyId) {
                "AWS Access Key ID is required for Rest configuration"
            }
        val awsSecretAccessKey =
            requireNotNull(config.awsAccessKeyConfiguration.secretAccessKey) {
                "AWS Secret Access Key is required for Rest configuration"
            }

        val restProperties = buildMap {
            put(CatalogUtil.ICEBERG_CATALOG_TYPE, ICEBERG_CATALOG_TYPE_REST)
            put(AwsClientProperties.CLIENT_REGION, region)
            put(URI, catalogConfig.serverUri)
            put(S3FileIOProperties.ACCESS_KEY_ID, awsAccessKeyId)
            put(S3FileIOProperties.SECRET_ACCESS_KEY, awsSecretAccessKey)
        }

        return restProperties + s3Properties
    }

    private fun buildS3Properties(
        config: GcsDataLakeConfiguration,
        icebergCatalogConfig: IcebergCatalogConfiguration,
    ): Map<String, String> {
        return buildMap {
            put(CatalogProperties.FILE_IO_IMPL, S3FileIO::class.java.name)
            put(S3FileIOProperties.PATH_STYLE_ACCESS, "true")
            put(CatalogProperties.WAREHOUSE_LOCATION, icebergCatalogConfig.warehouseLocation)

            // Add optional S3 endpoint if provided
            config.s3BucketConfiguration.s3Endpoint?.let { endpoint ->
                put(S3FileIOProperties.ENDPOINT, endpoint)
            }
        }
    }

    private fun buildNessieProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig: NessieCatalogConfiguration,
        s3Properties: Map<String, String>
    ): Map<String, String> {
        val awsAccessKeyId =
            requireNotNull(config.awsAccessKeyConfiguration.accessKeyId) {
                "AWS Access Key ID is required for Nessie configuration"
            }
        val awsSecretAccessKey =
            requireNotNull(config.awsAccessKeyConfiguration.secretAccessKey) {
                "AWS Secret Access Key is required for Nessie configuration"
            }

        val nessieProperties = buildMap {
            put(CatalogUtil.ICEBERG_CATALOG_TYPE, ICEBERG_CATALOG_TYPE_NESSIE)
            put(URI, catalogConfig.serverUri)
            put(
                NessieConfigConstants.CONF_NESSIE_REF,
                config.icebergCatalogConfiguration.mainBranchName
            )
            put(S3FileIOProperties.ACCESS_KEY_ID, awsAccessKeyId)
            put(S3FileIOProperties.SECRET_ACCESS_KEY, awsSecretAccessKey)

            // Add optional Nessie authentication if provided
            catalogConfig.accessToken?.let { token ->
                put(NessieConfigConstants.CONF_NESSIE_AUTH_TYPE, "BEARER")
                put(NessieConfigConstants.CONF_NESSIE_AUTH_TOKEN, token)
            }
        }

        return nessieProperties + s3Properties
    }

    private fun buildGlueProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig: GlueCatalogConfiguration,
        icebergCatalogConfig: IcebergCatalogConfiguration,
        region: String,
    ): Map<String, String> {
        val baseGlueProperties =
            mapOf(
                CatalogUtil.ICEBERG_CATALOG_TYPE to ICEBERG_CATALOG_TYPE_GLUE,
                CatalogProperties.WAREHOUSE_LOCATION to icebergCatalogConfig.warehouseLocation,
                AwsProperties.GLUE_CATALOG_ID to catalogConfig.glueId,
                AwsClientProperties.CLIENT_REGION to region,
            )

        val clientProperties =
            if (catalogConfig.awsArnRoleConfiguration.roleArn != null) {
                buildRoleBasedClientProperties(
                    catalogConfig.awsArnRoleConfiguration.roleArn!!,
                    config
                )
            } else {
                buildKeyBasedClientProperties(config)
            }

        return baseGlueProperties + clientProperties
    }

    private fun buildKeyBasedClientProperties(
        config: GcsDataLakeConfiguration
    ): Map<String, String> {
        val clientCredentialsProviderPrefix = "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}."

        val properties =
            mutableMapOf(
                AwsClientProperties.CLIENT_REGION to
                    config.s3BucketConfiguration.s3BucketRegion.region,
                AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER to
                    GlueCredentialsProvider::class.java.name,
                "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}.$AWS_CREDENTIALS_MODE" to
                    AWS_CREDENTIALS_MODE_STATIC_CREDS,
            )

        // If we don't have explicit S3 creds, fall back to the default creds provider chain.
        // For example, this should allow us to use AWS instance profiles.
        val awsAccessKeyId = config.awsAccessKeyConfiguration.accessKeyId
        val awsSecretAccessKey = config.awsAccessKeyConfiguration.secretAccessKey
        if (awsAccessKeyId != null && awsSecretAccessKey != null) {
            properties[S3FileIOProperties.ACCESS_KEY_ID] = awsAccessKeyId
            properties[S3FileIOProperties.SECRET_ACCESS_KEY] = awsSecretAccessKey
            properties["${clientCredentialsProviderPrefix}${ACCESS_KEY_ID}"] = awsAccessKeyId
            properties["${clientCredentialsProviderPrefix}${SECRET_ACCESS_KEY}"] =
                awsSecretAccessKey
        }

        return properties
    }
}
