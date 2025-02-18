/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.s3_data_lake.ACCESS_KEY_ID
import io.airbyte.integrations.destination.s3_data_lake.ASSUME_ROLE_ARN
import io.airbyte.integrations.destination.s3_data_lake.ASSUME_ROLE_EXTERNAL_ID
import io.airbyte.integrations.destination.s3_data_lake.ASSUME_ROLE_REGION
import io.airbyte.integrations.destination.s3_data_lake.AWS_CREDENTIALS_MODE
import io.airbyte.integrations.destination.s3_data_lake.AWS_CREDENTIALS_MODE_ASSUME_ROLE
import io.airbyte.integrations.destination.s3_data_lake.AWS_CREDENTIALS_MODE_STATIC_CREDS
import io.airbyte.integrations.destination.s3_data_lake.GlueCredentialsProvider
import io.airbyte.integrations.destination.s3_data_lake.S3DataLakeConfiguration
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
class S3DataLakeUtil(
    private val icebergUtil: IcebergUtil,
    private val assumeRoleCredentials: AwsAssumeRoleCredentials?,
) {
    fun createNamespaceWithGlueHandling(
        streamDescriptor: DestinationStream.Descriptor,
        catalog: Catalog
    ) {
        try {
            icebergUtil.createNamespace(streamDescriptor, catalog)
        } catch (e: ConcurrentModificationException) {
            // glue catalog throws its own special exception
            logger.info {
                "Namespace '${streamDescriptor.namespace}' was likely created by another thread during parallel operations."
            }
        }
    }

    /**
     * Creates the Iceberg [Catalog] configuration properties from the destination's configuration.
     *
     * @param config The destination's configuration
     * @return The Iceberg [Catalog] configuration properties.
     */
    fun toCatalogProperties(config: S3DataLakeConfiguration): Map<String, String> {
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
        config: S3DataLakeConfiguration,
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
        config: S3DataLakeConfiguration,
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
        config: S3DataLakeConfiguration,
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
        config: S3DataLakeConfiguration,
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

    private fun buildRoleBasedClientProperties(
        roleArn: String,
        config: S3DataLakeConfiguration
    ): Map<String, String> {
        val region = config.s3BucketConfiguration.s3BucketRegion.region
        val (accessKeyId, secretAccessKey, externalId) =
            if (assumeRoleCredentials != null) {
                Triple(
                    assumeRoleCredentials.accessKey,
                    assumeRoleCredentials.secretKey,
                    assumeRoleCredentials.externalId,
                )
            } else {
                throw IllegalStateException(
                    "Cannot assume role without system-provided credentials"
                )
            }

        return mapOf(
            // Note: no explicit credentials, whether on AwsProperties.REST_ACCESS_KEY_ID, or on
            // S3FileIOProperties.ACCESS_KEY_ID.
            // If you set S3FileIOProperties.ACCESS_KEY_ID, it causes the iceberg SDK to use those
            // credentials
            // _instead_ of the explicit GlueCredentialsProvider.
            // Note that we are _not_ setting any of the AwsProperties.CLIENT_ASSUME_ROLE_XYZ
            // properties - this is because we're manually handling the assume role stuff within
            // GlueCredentialsProvider.
            // And we're doing it ourselves because the built-in handling (i.e. setting
            // `AwsProperties.CLIENT_FACTORY to AssumeRoleAwsClientFactory::class.java.name`)
            // has some bad behavior (there's no way to actually set the bootstrap credentials
            // on the STS client, so you have to do a
            // `System.setProperty(access key, secret key, external ID)`)
            AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER to
                GlueCredentialsProvider::class.java.name,
            "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}.$AWS_CREDENTIALS_MODE" to
                AWS_CREDENTIALS_MODE_ASSUME_ROLE,
            "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}.$ACCESS_KEY_ID" to accessKeyId,
            "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}.$SECRET_ACCESS_KEY" to
                secretAccessKey,
            "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}.$ASSUME_ROLE_ARN" to roleArn,
            "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}.$ASSUME_ROLE_EXTERNAL_ID" to
                externalId,
            "${AwsClientProperties.CLIENT_CREDENTIALS_PROVIDER}.$ASSUME_ROLE_REGION" to region,
        )
    }

    private fun buildKeyBasedClientProperties(
        config: S3DataLakeConfiguration
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
