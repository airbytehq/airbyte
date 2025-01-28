/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.command.iceberg.parquet.DremioCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergRecord
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
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
import io.airbyte.integrations.destination.s3_data_lake.TableIdGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogProperties.URI
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_GLUE
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_NESSIE
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_REST
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.SortOrder
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties.DEFAULT_FILE_FORMAT
import org.apache.iceberg.aws.AwsClientProperties
import org.apache.iceberg.aws.AwsProperties
import org.apache.iceberg.aws.s3.S3FileIO
import org.apache.iceberg.aws.s3.S3FileIOProperties
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.SupportsNamespaces
import org.apache.iceberg.data.Record
import org.apache.iceberg.exceptions.AlreadyExistsException
import org.projectnessie.client.NessieConfigConstants
import software.amazon.awssdk.services.glue.model.ConcurrentModificationException

private val logger = KotlinLogging.logger {}

const val AIRBYTE_CDC_DELETE_COLUMN = "_ab_cdc_deleted_at"
private const val AWS_REGION = "aws.region"

/**
 * Collection of Iceberg related utilities.
 * @param awsSystemCredentials is a temporary fix to allow us to run the integrations tests. This
 * will be removed when we change all of this to use Micronaut
 */
@Singleton
class S3DataLakeUtil(
    private val tableIdGenerator: TableIdGenerator,
    private val assumeRoleCredentials: AwsAssumeRoleCredentials?,
) {

    internal class InvalidFormatException(message: String) : Exception(message)

    private val generationIdRegex = Regex("""ab-generation-id-\d+-e""")

    fun assertGenerationIdSuffixIsOfValidFormat(generationId: String) {
        if (!generationIdRegex.matches(generationId)) {
            throw InvalidFormatException(
                "Invalid format: $generationId. Expected format is 'ab-generation-id-<number>-e'",
            )
        }
    }

    fun constructGenerationIdSuffix(stream: DestinationStream): String {
        return constructGenerationIdSuffix(stream.generationId)
    }

    fun constructGenerationIdSuffix(generationId: Long): String {
        if (generationId < 0) {
            throw IllegalArgumentException(
                "GenerationId must be non-negative. Provided: $generationId",
            )
        }
        return "ab-generation-id-${generationId}-e"
    }
    /**
     * Builds an Iceberg [Catalog].
     *
     * @param catalogName The name of the catalog.
     * @param properties The map of catalog configuration properties.
     * @return The configured Iceberg [Catalog].
     */
    fun createCatalog(catalogName: String, properties: Map<String, String>): Catalog {
        return CatalogUtil.buildIcebergCatalog(catalogName, properties, Configuration())
    }

    /**
     * Builds (if necessary) an Iceberg [Table]. This includes creating the table's namespace if it
     * does not already exist. If the [Table] already exists, it is loaded from the [Catalog].
     *
     * @param streamDescriptor The [DestinationStream.Descriptor] that contains the Airbyte stream's
     * namespace and name.
     * @param catalog The Iceberg [Catalog] that contains the [Table] or should contain it once
     * created.
     * @param schema The Iceberg [Schema] associated with the [Table].
     * @param properties The [Table] configuration properties derived from the [Catalog].
     * @return The Iceberg [Table], created if it does not yet exist.
     */
    fun createTable(
        streamDescriptor: DestinationStream.Descriptor,
        catalog: Catalog,
        schema: Schema,
        properties: Map<String, String>
    ): Table {
        val tableIdentifier = tableIdGenerator.toTableIdentifier(streamDescriptor)
        synchronized(tableIdentifier.namespace()) {
            if (
                catalog is SupportsNamespaces &&
                    !catalog.namespaceExists(tableIdentifier.namespace())
            ) {
                try {
                    catalog.createNamespace(tableIdentifier.namespace())
                    logger.info { "Created namespace '${tableIdentifier.namespace()}'." }
                } catch (e: AlreadyExistsException) {
                    // This exception occurs when multiple threads attempt to write to the same
                    // namespace in parallel.
                    // One thread may create the namespace successfully, causing the other threads
                    // to encounter this exception
                    // when they also try to create the namespace.
                    logger.info {
                        "Namespace '${tableIdentifier.namespace()}' was likely created by another thread during parallel operations."
                    }
                } catch (e: ConcurrentModificationException) {
                    // do the same for AWS Glue
                    logger.info {
                        "Namespace '${tableIdentifier.namespace()}' was likely created by another thread during parallel operations."
                    }
                }
            }
        }

        return if (!catalog.tableExists(tableIdentifier)) {
            logger.info { "Creating Iceberg table '$tableIdentifier'...." }
            catalog
                .buildTable(tableIdentifier, schema)
                .withProperties(properties)
                .withProperty(DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase())
                .withSortOrder(getSortOrder(schema = schema))
                .create()
        } else {
            logger.info { "Loading Iceberg table $tableIdentifier ..." }
            catalog.loadTable(tableIdentifier)
        }
    }

    /**
     * Converts an Airbyte [DestinationRecordAirbyteValue] into an Iceberg [Record]. The converted
     * record will be wrapped to include [Operation] information, which is used by the writer to
     * determine how to write the data to the underlying Iceberg files.
     *
     * @param record The Airbyte [DestinationRecordAirbyteValue] record to be converted for writing
     * by Iceberg.
     * @param stream The Airbyte [DestinationStream] that contains information about the stream.
     * @param tableSchema The Iceberg [Table] [Schema].
     * @param pipeline The [MapperPipeline] used to convert the Airbyte record to an Iceberg record.
     * @return An Iceberg [Record] representation of the Airbyte [DestinationRecordAirbyteValue].
     */
    fun toRecord(
        record: DestinationRecordAirbyteValue,
        stream: DestinationStream,
        tableSchema: Schema,
        pipeline: MapperPipeline
    ): Record {
        val dataMapped =
            pipeline
                .map(record.data, record.meta?.changes)
                .withAirbyteMeta(stream, record.emittedAtMs, true)
        // TODO figure out how to detect the actual operation value
        return RecordWrapper(
            delegate = dataMapped.toIcebergRecord(tableSchema),
            operation = getOperation(record = record, importType = stream.importType)
        )
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
            is RestCatalogConfiguration -> buildRestProperties(config, catalogConfig, s3Properties)
            is DremioCatalogConfiguration ->
                catalogConfig.getCatalogProperties(icebergCatalogConfig)
            else ->
                throw IllegalArgumentException(
                    "Unsupported catalog type: ${catalogConfig::class.java.name}"
                )
        }
    }

    private fun buildRestProperties(
        config: S3DataLakeConfiguration,
        catalogConfig: RestCatalogConfiguration,
        s3Properties: Map<String, String>
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

    fun toIcebergSchema(stream: DestinationStream, pipeline: MapperPipeline): Schema {
        val primaryKeys =
            when (stream.importType) {
                is Dedupe -> (stream.importType as Dedupe).primaryKey
                else -> emptyList()
            }
        return pipeline.finalSchema.withAirbyteMeta(true).toIcebergSchema(primaryKeys)
    }

    private fun getSortOrder(schema: Schema): SortOrder {
        val builder = SortOrder.builderFor(schema)
        schema.identifierFieldNames().forEach { builder.asc(it) }
        return builder.build()
    }

    private fun getOperation(
        record: DestinationRecordAirbyteValue,
        importType: ImportType,
    ): Operation =
        if (
            record.data is ObjectValue &&
                (record.data as ObjectValue).values[AIRBYTE_CDC_DELETE_COLUMN] != null &&
                (record.data as ObjectValue).values[AIRBYTE_CDC_DELETE_COLUMN] !is NullValue
        ) {
            Operation.DELETE
        } else if (importType is Dedupe) {
            Operation.UPDATE
        } else {
            Operation.INSERT
        }
}
