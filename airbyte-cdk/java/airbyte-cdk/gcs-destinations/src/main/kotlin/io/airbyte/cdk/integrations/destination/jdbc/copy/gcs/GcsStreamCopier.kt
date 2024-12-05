/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy.gcs

import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.WriteChannel
import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
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
import java.io.ByteArrayInputStream
import java.io.IOException
import java.io.InputStream
import java.io.PrintWriter
import java.nio.channels.Channels
import java.nio.charset.StandardCharsets
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.util.*
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val LOGGER = KotlinLogging.logger {}

abstract class GcsStreamCopier(
    protected val stagingFolder: String,
    private val destSyncMode: DestinationSyncMode,
    protected val schemaName: String,
    protected val streamName: String,
    private val storageClient: Storage,
    protected val db: JdbcDatabase,
    protected val gcsConfig: GcsConfig,
    private val nameTransformer: StandardNameTransformer,
    private val sqlOperations: SqlOperations
) : StreamCopier {
    @get:VisibleForTesting
    val tmpTableName: String = @Suppress("deprecation") nameTransformer.getTmpTableName(streamName)
    protected val gcsStagingFiles: MutableSet<String> = HashSet()
    protected var filenameGenerator: StagingFilenameGenerator =
        StagingFilenameGenerator(
            streamName,
            GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES.toLong()
        )
    private val channels = HashMap<String, WriteChannel>()
    private val csvPrinters = HashMap<String, CSVPrinter>()

    private fun prepareGcsStagingFile(): String {
        return java.lang.String.join(
            "/",
            stagingFolder,
            schemaName,
            filenameGenerator.stagingFilename
        )
    }

    override fun prepareStagingFile(): String {
        val name = prepareGcsStagingFile()
        if (!gcsStagingFiles.contains(name)) {
            gcsStagingFiles.add(name)
            val blobId = BlobId.of(gcsConfig.bucketName, name)
            val blobInfo = BlobInfo.newBuilder(blobId).build()
            val blob = storageClient.create(blobInfo)
            val channel = blob.writer()
            channels[name] = channel
            val outputStream = Channels.newOutputStream(channel)

            val writer = PrintWriter(outputStream, true, StandardCharsets.UTF_8)
            try {
                csvPrinters[name] = CSVPrinter(writer, CSVFormat.DEFAULT)
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
        }
        return name
    }

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

    @Throws(Exception::class)
    override fun closeNonCurrentStagingFileWriters() {
        // TODO need to update this method when updating whole class for using GcsWriter
    }

    @Throws(Exception::class)
    override fun closeStagingUploader(hasFailed: Boolean) {
        LOGGER.info { "Uploading remaining data for $streamName stream." }
        for (csvPrinter in csvPrinters.values) {
            csvPrinter.close()
        }
        for (channel in channels.values) {
            channel.close()
        }
        LOGGER.info { "All data for $streamName stream uploaded." }
    }

    @Throws(Exception::class)
    override fun copyStagingFileToTemporaryTable() {
        LOGGER.info {
            "Starting copy to tmp table: $tmpTableName in destination for stream: $streamName, schema: $schemaName."
        }
        for (gcsStagingFile in gcsStagingFiles) {
            copyGcsCsvFileIntoTable(
                db,
                getFullGcsPath(gcsConfig.bucketName, gcsStagingFile),
                schemaName,
                tmpTableName,
                gcsConfig
            )
        }
        LOGGER.info {
            "Copy to tmp table $tmpTableName in destination for stream $streamName complete."
        }
    }

    @Throws(Exception::class)
    override fun removeFileAndDropTmpTable() {
        for (gcsStagingFile in gcsStagingFiles) {
            LOGGER.info { "Begin cleaning gcs staging file $gcsStagingFile." }
            val blobId = BlobId.of(gcsConfig.bucketName, gcsStagingFile)
            if (storageClient[blobId].exists()) {
                storageClient.delete(blobId)
            }
            LOGGER.info { "GCS staging file $gcsStagingFile cleaned." }
        }

        LOGGER.info { "Begin cleaning $tmpTableName tmp table in destination." }
        sqlOperations.dropTableIfExists(db, schemaName, tmpTableName)
        LOGGER.info { "$tmpTableName tmp table in destination cleaned." }
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
    override fun createDestinationTable(): String {
        val destTableName = @Suppress("deprecation") nameTransformer.getRawTableName(streamName)
        LOGGER.info { "Preparing table $destTableName in destination." }
        sqlOperations.createTableIfNotExists(db, schemaName, destTableName)
        LOGGER.info { "Table $tmpTableName in destination prepared." }

        return destTableName
    }

    @Throws(Exception::class)
    override fun generateMergeStatement(destTableName: String): String {
        LOGGER.info {
            "Preparing to merge tmp table $tmpTableName to dest table: $destTableName, schema: $schemaName, in destination."
        }
        val queries = StringBuilder()
        if (destSyncMode == DestinationSyncMode.OVERWRITE) {
            queries.append(sqlOperations.truncateTableQuery(db, schemaName, destTableName))
            LOGGER.info {
                "Destination OVERWRITE mode detected. Dest table: $destTableName, schema: $schemaName, will be truncated."
            }
        }
        queries.append(sqlOperations.insertTableQuery(db, schemaName, tmpTableName, destTableName))
        return queries.toString()
    }

    override val currentFile: String?
        get() = // TODO need to update this method when updating whole class for using GcsWriter
        null

    @Throws(SQLException::class)
    abstract fun copyGcsCsvFileIntoTable(
        database: JdbcDatabase?,
        gcsFileLocation: String?,
        schema: String?,
        tableName: String?,
        gcsConfig: GcsConfig?
    )

    companion object {

        // It is optimal to write every 10,000,000 records (BATCH_SIZE * MAX_PER_FILE_PART_COUNT) to
        // a new
        // file.
        // The BATCH_SIZE is defined in CopyConsumerFactory.
        // The average size of such a file will be about 1 GB.
        // This will make it easier to work with files and speed up the recording of large amounts
        // of data.
        // In addition, for a large number of records, we will not get a drop in the copy request to
        // QUERY_TIMEOUT when
        // the records from the file are copied to the staging table.
        const val MAX_PARTS_PER_FILE: Int = 1000
        private fun getFullGcsPath(bucketName: String?, stagingFile: String): String {
            // this is intentionally gcs:/ not gcs:// since the join adds the additional slash
            return java.lang.String.join("/", "gcs:/", bucketName, stagingFile)
        }

        @Throws(IOException::class)
        fun attemptWriteToPersistence(gcsConfig: GcsConfig) {
            val outputTableName =
                "_airbyte_connection_test_" +
                    UUID.randomUUID().toString().replace("-".toRegex(), "")
            attemptWriteAndDeleteGcsObject(gcsConfig, outputTableName)
        }

        @Throws(IOException::class)
        private fun attemptWriteAndDeleteGcsObject(gcsConfig: GcsConfig, outputTableName: String) {
            val storage = getStorageClient(gcsConfig)
            val blobId = BlobId.of(gcsConfig.bucketName, "check-content/$outputTableName")
            val blobInfo = BlobInfo.newBuilder(blobId).build()

            storage.create(blobInfo, "".toByteArray(StandardCharsets.UTF_8))
            storage.delete(blobId)
        }

        @Throws(IOException::class)
        fun getStorageClient(gcsConfig: GcsConfig): Storage {
            val credentialsInputStream: InputStream =
                ByteArrayInputStream(gcsConfig.credentialsJson.toByteArray(StandardCharsets.UTF_8))
            val credentials = GoogleCredentials.fromStream(credentialsInputStream)
            return StorageOptions.newBuilder()
                .setCredentials(credentials)
                .setProjectId(gcsConfig.projectId)
                .build()
                .service
        }
    }
}
