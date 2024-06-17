/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.BigQueryOptions
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
import com.google.common.base.Charsets
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler.Companion.addAllStringsInConfigForDeinterpolation
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler.Companion.addThrowableForDeinterpolation
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.JavaBaseConstants.DestinationColumns.*
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.getRawNamespaceOverride
import io.airbyte.cdk.integrations.destination.gcs.BaseGcsDestination
import io.airbyte.cdk.integrations.destination.gcs.GcsNameTransformer
import io.airbyte.cdk.integrations.destination.gcs.GcsStorageOperations
import io.airbyte.cdk.integrations.destination.operation.SyncOperation
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.staging.operation.StagingStreamOperations
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons.serialize
import io.airbyte.commons.json.Jsons.tryDeserialize
import io.airbyte.integrations.base.destination.operation.DefaultSyncOperation
import io.airbyte.integrations.base.destination.operation.StandardStreamOperation
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.destination.bigquery.BigQueryConsts as bqConstants
import io.airbyte.integrations.destination.bigquery.BigQueryConsumerFactory.createDirectUploadConsumer
import io.airbyte.integrations.destination.bigquery.BigQueryConsumerFactory.createStagingConsumer
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.*
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.migrators.BigQueryDV2Migration
import io.airbyte.integrations.destination.bigquery.migrators.BigQueryDestinationState
import io.airbyte.integrations.destination.bigquery.migrators.BigqueryAirbyteMetaAndGenerationIdMigration
import io.airbyte.integrations.destination.bigquery.operation.BigQueryDirectLoadingStorageOperation
import io.airbyte.integrations.destination.bigquery.operation.BigQueryGcsStorageOperation
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.IOException
import java.util.*
import java.util.function.Consumer

private val log = KotlinLogging.logger {}

class BigQueryDestination : BaseConnector(), Destination {

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            val datasetId = getDatasetId(config)
            val datasetLocation = getDatasetLocation(config)
            val bigquery = getBigQuery(config)
            val uploadingMethod = getLoadingMethod(config)

            checkHasCreateAndDeleteDatasetRole(bigquery, datasetId, datasetLocation)

            val dataset = getOrCreateDataset(bigquery, datasetId, datasetLocation)
            if (dataset.location != datasetLocation) {
                throw ConfigErrorException(
                    "Actual dataset location doesn't match to location from config",
                )
            }
            val queryConfig =
                QueryJobConfiguration.newBuilder(
                        String.format(
                            "SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES` LIMIT 1;",
                            datasetId,
                        ),
                    )
                    .setUseLegacySql(false)
                    .build()

            if (UploadingMethod.GCS == uploadingMethod) {
                val status = checkGcsPermission(config)
                if (status!!.status != AirbyteConnectionStatus.Status.SUCCEEDED) {
                    return status
                }
            }

            val result = executeQuery(bigquery, queryConfig)
            if (result.getLeft() != null) {
                return AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
            } else {
                throw ConfigErrorException(result.getRight())
            }
        } catch (e: Exception) {
            log.error(e) { "Check failed." }
            throw ConfigErrorException((if (e.message != null) e.message else e.toString())!!)
        }
    }

    /**
     * This method does two checks: 1) permissions related to the bucket, and 2) the ability to
     * create and delete an actual file. The latter is important because even if the service account
     * may have the proper permissions, the HMAC keys can only be verified by running the actual GCS
     * check.
     */
    private fun checkGcsPermission(config: JsonNode): AirbyteConnectionStatus? {
        val loadingMethod = config[bqConstants.LOADING_METHOD]
        val bucketName = loadingMethod[bqConstants.GCS_BUCKET_NAME].asText()
        val missingPermissions: MutableList<String> = ArrayList()

        try {
            val credentials = getServiceAccountCredentials(config)
            val storage: Storage =
                StorageOptions.newBuilder()
                    .setProjectId(config[bqConstants.CONFIG_PROJECT_ID].asText())
                    .setCredentials(credentials)
                    .setHeaderProvider(getHeaderProvider())
                    .build()
                    .service
            val permissionsCheckStatusList: List<Boolean> =
                storage.testIamPermissions(bucketName, REQUIRED_PERMISSIONS)

            // testIamPermissions returns a list of booleans
            // in the same order of the presented permissions list
            missingPermissions.addAll(
                permissionsCheckStatusList
                    .asSequence()
                    .withIndex()
                    .filter { !it.value }
                    .map { REQUIRED_PERMISSIONS[it.index] }
                    .toList(),
            )

            val gcsDestination: BaseGcsDestination = object : BaseGcsDestination() {}
            val gcsJsonNodeConfig = getGcsJsonNodeConfig(config)
            return gcsDestination.check(gcsJsonNodeConfig)
        } catch (e: Exception) {
            val message = StringBuilder("Cannot access the GCS bucket.")
            if (!missingPermissions.isEmpty()) {
                message
                    .append(" The following permissions are missing on the service account: ")
                    .append(java.lang.String.join(", ", missingPermissions))
                    .append(".")
            }
            message.append(
                " Please make sure the service account can access the bucket path, and the HMAC keys are correct.",
            )

            log.error(e) { message.toString() }
            throw ConfigErrorException(
                "Could not access the GCS bucket with the provided configuration.\n",
                e,
            )
        }
    }

    /**
     * Returns a [AirbyteMessageConsumer] based on whether the uploading mode is STANDARD INSERTS or
     * using STAGING
     *
     * @param config
     * - integration-specific configuration object as json. e.g. { "username": "airbyte",
     * "password": "super secure" }
     * @param catalog
     * - schema of the incoming messages.
     */
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw UnsupportedOperationException("Should use getSerializedMessageConsumer")
    }

    @Throws(Exception::class)
    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {
        val uploadingMethod = getLoadingMethod(config)
        val defaultNamespace = getDatasetId(config)
        val disableTypeDedupe = getDisableTypeDedupFlag(config)
        val datasetLocation = getDatasetLocation(config)
        val projectId = config[bqConstants.CONFIG_PROJECT_ID].asText()
        val bigquery = getBigQuery(config)
        val rawNamespaceOverride = getRawNamespaceOverride(bqConstants.RAW_DATA_DATASET)

        addAllStringsInConfigForDeinterpolation(config)
        val serviceAccountKey = config[bqConstants.CONFIG_CREDS]
        if (serviceAccountKey != null) {
            // If the service account key is a non-null string, we will try to
            // deserialize it. Otherwise, we will let the Google library find it in
            // the environment during the client initialization.
            if (serviceAccountKey.isTextual) {
                // There are cases where we fail to deserialize the service account key. In these
                // cases, we
                // shouldn't do anything.
                // Google's creds library is more lenient with JSON-parsing than Jackson, and I'd
                // rather just let it
                // go.
                tryDeserialize(serviceAccountKey.asText()).ifPresent { obj: JsonNode ->
                    addAllStringsInConfigForDeinterpolation(obj)
                }
            } else {
                addAllStringsInConfigForDeinterpolation(serviceAccountKey)
            }
        }

        val sqlGenerator = BigQuerySqlGenerator(projectId, datasetLocation)
        val parsedCatalog =
            parseCatalog(
                sqlGenerator,
                defaultNamespace,
                rawNamespaceOverride.orElse(JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE),
                catalog,
            )
        val destinationHandler = BigQueryDestinationHandler(bigquery, datasetLocation)

        val migrations =
            listOf(
                BigQueryDV2Migration(sqlGenerator, bigquery),
                BigqueryAirbyteMetaAndGenerationIdMigration(bigquery),
            )

        if (uploadingMethod == UploadingMethod.STANDARD) {
            val bigQueryClientChunkSize = getBigQueryClientChunkSize(config)
            val bigQueryLoadingStorageOperation =
                BigQueryDirectLoadingStorageOperation(
                    bigquery,
                    bigQueryClientChunkSize,
                    BigQueryRecordFormatter(),
                    sqlGenerator,
                    destinationHandler,
                    datasetLocation,
                )
            val syncOperation =
                DefaultSyncOperation<BigQueryDestinationState>(
                    parsedCatalog,
                    destinationHandler,
                    defaultNamespace,
                    { initialStatus: DestinationInitialStatus<BigQueryDestinationState>, disableTD
                        ->
                        StandardStreamOperation(
                            bigQueryLoadingStorageOperation,
                            initialStatus,
                            disableTD
                        )
                    },
                    migrations,
                    disableTypeDedupe,
                )
            return createDirectUploadConsumer(
                outputRecordCollector,
                syncOperation,
                catalog,
                defaultNamespace,
            )
        }

        val gcsNameTransformer = GcsNameTransformer()
        val gcsConfig = getGcsCsvDestinationConfig(config)
        val keepStagingFiles = isKeepFilesInGcs(config)
        val gcsOperations =
            GcsStorageOperations(gcsNameTransformer, gcsConfig.getS3Client(), gcsConfig)

        val bigQueryGcsStorageOperations =
            BigQueryGcsStorageOperation(
                gcsOperations,
                gcsConfig,
                gcsNameTransformer,
                keepStagingFiles,
                bigquery,
                sqlGenerator,
                destinationHandler,
            )
        val syncOperation: SyncOperation =
            DefaultSyncOperation<BigQueryDestinationState>(
                parsedCatalog,
                destinationHandler,
                defaultNamespace,
                { initialStatus: DestinationInitialStatus<BigQueryDestinationState>, disableTD ->
                    StagingStreamOperations(
                        bigQueryGcsStorageOperations,
                        initialStatus,
                        FileUploadFormat.CSV,
                        V2_WITH_GENERATION,
                        disableTD
                    )
                },
                migrations,
                disableTypeDedupe,
            )
        return createStagingConsumer(
            outputRecordCollector,
            syncOperation,
            catalog,
            defaultNamespace,
        )
    }

    private fun parseCatalog(
        sqlGenerator: BigQuerySqlGenerator,
        defaultNamespace: String,
        rawNamespaceOverride: String,
        catalog: ConfiguredAirbyteCatalog
    ): ParsedCatalog {
        val catalogParser =
            CatalogParser(
                sqlGenerator,
                defaultNamespace = defaultNamespace,
                rawNamespace = rawNamespaceOverride,
            )

        return catalogParser.parseCatalog(catalog)
    }

    override val isV2Destination: Boolean
        get() = true

    companion object {

        private val REQUIRED_PERMISSIONS =
            listOf(
                "storage.multipartUploads.abort",
                "storage.multipartUploads.create",
                "storage.objects.create",
                "storage.objects.delete",
                "storage.objects.get",
                "storage.objects.list",
            )

        @JvmStatic
        fun getBigQuery(config: JsonNode): BigQuery {
            val projectId = config[bqConstants.CONFIG_PROJECT_ID].asText()

            try {
                val bigQueryBuilder = BigQueryOptions.newBuilder()
                val credentials = getServiceAccountCredentials(config)
                return bigQueryBuilder
                    .setProjectId(projectId)
                    .setCredentials(credentials)
                    .setHeaderProvider(getHeaderProvider())
                    .build()
                    .service
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
        }

        @JvmStatic
        @Throws(IOException::class)
        fun getServiceAccountCredentials(config: JsonNode): GoogleCredentials {
            val serviceAccountKey = config[bqConstants.CONFIG_CREDS]
            // Follows this order of resolution:
            // https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault
            if (serviceAccountKey == null) {
                log.info {
                    "No service account key json is provided. It is required if you are using Airbyte cloud."
                }
                log.info { "Using the default service account credential from environment." }
                return GoogleCredentials.getApplicationDefault()
            }

            // The JSON credential can either be a raw JSON object, or a serialized JSON object.
            val credentialsString =
                if (serviceAccountKey.isObject) serialize(serviceAccountKey)
                else serviceAccountKey.asText()
            return GoogleCredentials.fromStream(
                ByteArrayInputStream(credentialsString.toByteArray(Charsets.UTF_8)),
            )
        }
    }
}

fun main(args: Array<String>) {
    addThrowableForDeinterpolation(BigQueryException::class.java)
    val destination: Destination = BigQueryDestination()
    log.info { "Starting Destination : ${destination.javaClass}" }
    IntegrationRunner(destination).run(args)
    log.info { "Completed Destination : ${destination.javaClass}" }
}
