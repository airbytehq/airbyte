/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy.azure

import com.azure.storage.blob.BlobContainerClient
import com.azure.storage.blob.models.BlobItem
import com.azure.storage.blob.specialized.AppendBlobClient
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.cdk.integrations.destination.jdbc.StagingFilenameGenerator
import io.airbyte.cdk.integrations.destination.jdbc.constants.GlobalDataSizeConstants
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopier
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.*
import java.nio.charset.StandardCharsets
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.util.*
import java.util.function.Consumer
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val LOGGER = KotlinLogging.logger {}

abstract class AzureBlobStorageStreamCopier(
    protected val stagingFolder: String,
    private val destSyncMode: DestinationSyncMode,
    protected val schemaName: String,
    protected val streamName: String,
    private val specializedBlobClientBuilder: SpecializedBlobClientBuilder,
    protected val db: JdbcDatabase,
    protected val azureBlobConfig: AzureBlobStorageConfig,
    private val nameTransformer: StandardNameTransformer,
    private val sqlOperations: SqlOperations
) : StreamCopier {
    protected var filenameGenerator: StagingFilenameGenerator =
        StagingFilenameGenerator(
            streamName,
            GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES.toLong()
        )
    protected val azureStagingFiles: MutableSet<String> = HashSet()

    @Suppress("DEPRECATION")
    @get:VisibleForTesting
    val tmpTableName: String = nameTransformer.getTmpTableName(streamName)
    protected val activeStagingWriterFileNames: MutableSet<String> = HashSet()
    private val csvPrinters = HashMap<String, CSVPrinter>()
    private val blobClients = HashMap<String, AppendBlobClient>()
    override var currentFile: String? = null

    @Throws(Exception::class)
    override fun write(id: UUID?, recordMessage: AirbyteRecordMessage?, fileName: String?) {
        if (csvPrinters.containsKey(fileName)) {
            csvPrinters[fileName]!!.printRecord(
                id,
                Jsons.serialize(recordMessage!!.data),
                Timestamp.from(Instant.ofEpochMilli(recordMessage.emittedAt))
            )
        }
    }

    override fun prepareStagingFile(): String {
        currentFile = prepareAzureStagingFile()
        val currentFile = this.currentFile!!
        if (!azureStagingFiles.contains(currentFile)) {
            azureStagingFiles.add(currentFile)
            activeStagingWriterFileNames.add(currentFile)

            val appendBlobClient =
                specializedBlobClientBuilder.blobName(currentFile).buildAppendBlobClient()
            blobClients[currentFile] = appendBlobClient
            appendBlobClient.create(true)

            val bufferedOutputStream =
                BufferedOutputStream(
                    appendBlobClient.blobOutputStream,
                    Math.toIntExact(GlobalDataSizeConstants.MAX_FILE_SIZE)
                )
            val writer = PrintWriter(bufferedOutputStream, true, StandardCharsets.UTF_8)
            try {
                csvPrinters[currentFile] = CSVPrinter(writer, CSVFormat.DEFAULT)
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
        }
        return currentFile
    }

    private fun prepareAzureStagingFile(): String {
        return java.lang.String.join(
            "/",
            stagingFolder,
            schemaName,
            filenameGenerator.stagingFilename
        )
    }

    @Throws(Exception::class)
    override fun closeStagingUploader(hasFailed: Boolean) {
        LOGGER.info { "Uploading remaining data for $streamName stream." }
        for (csvPrinter in csvPrinters.values) {
            csvPrinter.close()
        }
        LOGGER.info { "All data for $streamName stream uploaded." }
    }

    @Throws(Exception::class)
    override fun createDestinationSchema() {
        LOGGER.info { "Creating schema in destination if it doesn't exist: $schemaName" }
        sqlOperations.createSchemaIfNotExists(db, schemaName)
    }

    @Throws(Exception::class)
    override fun createTemporaryTable() {
        LOGGER.info {
            "Preparing tmp table in destination for stream: $streamName, schema: $schemaName, tmp table name: $tmpTableName."
        }
        sqlOperations.createTableIfNotExists(db, schemaName, tmpTableName)
    }

    @Throws(Exception::class)
    override fun copyStagingFileToTemporaryTable() {
        LOGGER.info {
            "Starting copy to tmp table: $tmpTableName in destination for stream: $streamName, schema: $schemaName."
        }
        for (azureStagingFile in azureStagingFiles) {
            copyAzureBlobCsvFileIntoTable(
                db,
                getFullAzurePath(azureStagingFile),
                schemaName,
                tmpTableName,
                azureBlobConfig
            )
        }
        LOGGER.info {
            "Copy to tmp table $tmpTableName in destination for stream $streamName complete."
        }
    }

    private fun getFullAzurePath(azureStagingFile: String?): String {
        return ("azure://" +
            azureBlobConfig.accountName +
            "." +
            azureBlobConfig.endpointDomainName +
            "/" +
            azureBlobConfig.containerName +
            "/" +
            azureStagingFile)
    }

    @Throws(Exception::class)
    override fun createDestinationTable(): String? {
        @Suppress("DEPRECATION") val destTableName = nameTransformer.getRawTableName(streamName)
        LOGGER.info { "Preparing table $destTableName in destination." }
        sqlOperations.createTableIfNotExists(db, schemaName, destTableName)
        LOGGER.info { "Table $tmpTableName in destination prepared." }

        return destTableName
    }

    @Throws(Exception::class)
    override fun generateMergeStatement(destTableName: String?): String {
        LOGGER.info {
            "Preparing to merge tmp table $tmpTableName to dest table: $destTableName, schema: $schemaName, in destination."
        }
        val queries = StringBuilder()
        if (destSyncMode == DestinationSyncMode.OVERWRITE) {
            queries.append(sqlOperations.truncateTableQuery(db, schemaName, destTableName))
            LOGGER.info {
                "Destination OVERWRITE mode detected. Dest table: $destTableName, schema: $schemaName, truncated."
            }
        }
        queries.append(sqlOperations.insertTableQuery(db, schemaName, tmpTableName, destTableName))
        return queries.toString()
    }

    @Throws(Exception::class)
    override fun removeFileAndDropTmpTable() {
        LOGGER.info { "Begin cleaning azure blob staging files." }
        for (appendBlobClient in blobClients.values) {
            appendBlobClient.delete()
        }
        LOGGER.info { "Azure Blob staging files cleaned." }

        LOGGER.info { "Begin cleaning $tmpTableName tmp table in destination." }
        sqlOperations.dropTableIfExists(db, schemaName, tmpTableName)
        LOGGER.info { "$tmpTableName tmp table in destination cleaned." }
    }

    @Throws(Exception::class)
    override fun closeNonCurrentStagingFileWriters() {
        LOGGER.info { "Begin closing non current file writers" }
        val removedKeys: MutableSet<String> = HashSet()
        for (key in activeStagingWriterFileNames) {
            if (key != currentFile) {
                csvPrinters[key]!!.close()
                csvPrinters.remove(key)
                removedKeys.add(key)
            }
        }
        activeStagingWriterFileNames.removeAll(removedKeys)
    }

    @Throws(SQLException::class)
    abstract fun copyAzureBlobCsvFileIntoTable(
        database: JdbcDatabase?,
        snowflakeAzureExternalStageName: String?,
        schema: String?,
        tableName: String?,
        config: AzureBlobStorageConfig?
    )

    companion object {

        fun attemptAzureBlobWriteAndDelete(config: AzureBlobStorageConfig) {
            var appendBlobClient: AppendBlobClient? = null
            try {
                appendBlobClient =
                    SpecializedBlobClientBuilder()
                        .endpoint(config.endpointUrl)
                        .sasToken(config.sasToken)
                        .containerName(config.containerName)
                        .blobName("testAzureBlob" + UUID.randomUUID())
                        .buildAppendBlobClient()

                val containerClient = getBlobContainerClient(appendBlobClient)
                writeTestDataIntoBlob(appendBlobClient)
                listCreatedBlob(containerClient)
            } finally {
                if (appendBlobClient != null && appendBlobClient.exists()) {
                    LOGGER.info { "Deleting blob: ${appendBlobClient.blobName}" }
                    appendBlobClient.delete()
                }
            }
        }

        private fun listCreatedBlob(containerClient: BlobContainerClient) {
            containerClient
                .listBlobs()
                .forEach(
                    Consumer { blobItem: BlobItem ->
                        LOGGER.info { "Blob name: ${blobItem.name} Snapshot: ${blobItem.snapshot}" }
                    }
                )
        }

        private fun writeTestDataIntoBlob(appendBlobClient: AppendBlobClient?) {
            val test = "test_data"
            LOGGER.info { "Writing test data to Azure Blob storage: $test" }
            val dataStream: InputStream =
                ByteArrayInputStream(test.toByteArray(StandardCharsets.UTF_8))

            val blobCommittedBlockCount =
                appendBlobClient!!
                    .appendBlock(dataStream, test.length.toLong())
                    .blobCommittedBlockCount

            LOGGER.info { "blobCommittedBlockCount: $blobCommittedBlockCount" }
        }

        private fun getBlobContainerClient(
            appendBlobClient: AppendBlobClient?
        ): BlobContainerClient {
            val containerClient = appendBlobClient!!.containerClient
            if (!containerClient.exists()) {
                containerClient.create()
            }

            if (!appendBlobClient.exists()) {
                appendBlobClient.create()
                LOGGER.info { "blobContainerClient created" }
            } else {
                LOGGER.info { "blobContainerClient already exists" }
            }
            return containerClient
        }
    }
}
