/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.operation

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer
import io.airbyte.integrations.destination.redshift.manifest.Entry
import io.airbyte.integrations.destination.redshift.manifest.Manifest
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.Optional
import java.util.UUID
import java.util.stream.Collectors

private val log = KotlinLogging.logger {}

class RedshiftStagingStorageOperation(
    private val s3Config: S3DestinationConfig,
    private val keepStagingFiles: Boolean,
    private val s3StorageOperations: S3StorageOperations,
    private val sqlGenerator: RedshiftSqlGenerator,
    private val destinationHandler: RedshiftDestinationHandler,
    private val dropCascade: Boolean,
) : StorageOperation<SerializableBuffer> {
    private val connectionId: UUID = UUID.randomUUID()
    private val writeDatetime: ZonedDateTime = Instant.now().atZone(ZoneOffset.UTC)
    private val objectMapper = ObjectMapper()

    override fun prepareStage(streamId: StreamId, suffix: String, replace: Boolean) {
        // create raw table
        destinationHandler.execute(Sql.of(createRawTableQuery(streamId, suffix)))
        if (replace) {
            destinationHandler.execute(Sql.of(truncateRawTableQuery(streamId, suffix)))
        }
        // create bucket for staging files
        s3StorageOperations.createBucketIfNotExists()
    }

    override fun overwriteStage(streamId: StreamId, suffix: String) {
        val cascadeClause = if (dropCascade) "CASCADE" else ""
        destinationHandler.execute(
            Sql.transactionally(
                """DROP TABLE IF EXISTS "${streamId.rawNamespace}"."${streamId.rawName}" $cascadeClause""",
                """ALTER TABLE "${streamId.rawNamespace}"."${streamId.rawName}$suffix" RENAME TO "${streamId.rawName}" """
            )
        )
    }

    override fun transferFromTempStage(streamId: StreamId, suffix: String) {
        destinationHandler.execute(
            // ALTER TABLE ... APPEND is an efficient way to move records from one table to another.
            // Instead of naively duplicating the data, it actually moves the underlying data
            // blocks.
            // (https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_TABLE_APPEND.html)
            // But it can't run inside transactions, so run these statements separately.
            Sql.separately(
                // Note for future developers:
                // ALTER TABLE ... APPEND has some interesting restrictions where both tables need
                // the exact same structure (clustering, columns, etc.), so if we want to change
                // those in the future, this might be tricky/annoying?
                // If we have issues at that point, we can always switch to a simple
                // `INSERT INTO ... SELECT * FROM ...` query.
                """
                ALTER TABLE "${streamId.rawNamespace}"."${streamId.rawName}"
                APPEND FROM "${streamId.rawNamespace}"."${streamId.rawName}$suffix"
                """.trimIndent(),
                // No need to drop cascade. If the user created a view on top of the temp raw table,
                // that would be pretty weird, and we should fail loudly.
                """DROP TABLE IF EXISTS "${streamId.rawNamespace}"."${streamId.rawName}$suffix" """,
            ),
            // Skip the case-sensitivity thing - ALTER TABLE ... APPEND can't be run in a
            // transaction, so we can't run the SET statement.
            // We're only working with schema/table names, so it's fine to just quote the
            // identifiers instead of relying on this option.
            forceCaseSensitiveIdentifier = false
        )
    }

    override fun getStageGeneration(streamId: StreamId, suffix: String): Long? {
        val generation =
            destinationHandler.query(
                """SELECT ${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID} FROM "${streamId.rawNamespace}"."${streamId.rawName}$suffix" LIMIT 1"""
            )
        if (generation.isEmpty()) {
            return null
        }

        return generation.first()[JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID]?.asLong() ?: 0
    }

    override fun writeToStage(
        streamConfig: StreamConfig,
        suffix: String,
        data: SerializableBuffer
    ) {
        val streamId = streamConfig.id
        val objectPath: String = getStagingPath(streamId)
        log.info {
            "Uploading records to for ${streamId.rawNamespace}.${streamId.rawName} to path $objectPath"
        }
        val filename =
            s3StorageOperations.uploadRecordsToBucket(
                data,
                streamId.rawNamespace,
                objectPath,
                streamConfig.generationId
            )

        log.info {
            "Starting copy to target table from stage: ${streamId.rawName}$suffix in destination from stage: $objectPath/$filename."
        }
        val manifestContents = createManifest(listOf(filename), objectPath)
        val manifestPath = putManifest(manifestContents, objectPath)
        executeCopy(
            manifestPath,
            destinationHandler,
            streamId.rawNamespace,
            streamId.rawName,
            suffix
        )
        log.info {
            "Copy to target table ${streamId.rawNamespace}.${streamId.rawName}$suffix in destination complete."
        }
    }

    override fun cleanupStage(streamId: StreamId) {
        if (keepStagingFiles) return
        val stagingRootPath = getStagingPath(streamId)
        log.info { "Cleaning up staging path at $stagingRootPath" }
        s3StorageOperations.dropBucketObject(stagingRootPath)
    }

    override fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean) {
        destinationHandler.execute(sqlGenerator.createTable(streamConfig, suffix, replace))
    }

    override fun softResetFinalTable(streamConfig: StreamConfig) {
        TyperDeduperUtil.executeSoftReset(
            sqlGenerator = sqlGenerator,
            destinationHandler = destinationHandler,
            streamConfig,
        )
    }

    override fun overwriteFinalTable(streamConfig: StreamConfig, tmpTableSuffix: String) {
        if (tmpTableSuffix.isNotBlank()) {
            log.info {
                "Overwriting table ${streamConfig.id.finalTableId(RedshiftSqlGenerator.QUOTE)} with ${
                    streamConfig.id.finalTableId(
                        RedshiftSqlGenerator.QUOTE,
                        tmpTableSuffix,
                    )
                }"
            }
            destinationHandler.execute(
                sqlGenerator.overwriteFinalTable(streamConfig.id, tmpTableSuffix)
            )
        }
    }

    override fun typeAndDedupe(
        streamConfig: StreamConfig,
        maxProcessedTimestamp: Optional<Instant>,
        finalTableSuffix: String
    ) {
        TyperDeduperUtil.executeTypeAndDedupe(
            sqlGenerator = sqlGenerator,
            destinationHandler = destinationHandler,
            streamConfig,
            maxProcessedTimestamp,
            finalTableSuffix,
        )
    }

    private fun getStagingPath(streamId: StreamId): String {
        // S3DestinationConfig.getS3DestinationConfig always sets a nonnull bucket path
        // TODO mark bucketPath as non-nullable
        val prefix =
            if (s3Config.bucketPath!!.isEmpty()) ""
            else s3Config.bucketPath + (if (s3Config.bucketPath!!.endsWith("/")) "" else "/")
        return nameTransformer.applyDefaultCase(
            String.format(
                "%s%s/%s_%02d_%02d_%02d_%s/",
                prefix,
                nameTransformer.applyDefaultCase(
                    // I have no idea why we're doing this.
                    // streamId.rawName already has been passed through the name transformer.
                    nameTransformer.convertStreamName(streamId.rawName)
                ),
                writeDatetime.year,
                writeDatetime.monthValue,
                writeDatetime.dayOfMonth,
                writeDatetime.hour,
                connectionId
            )
        )
    }

    private fun createManifest(stagedFiles: List<String>, stagingPath: String): String {
        if (stagedFiles.isEmpty()) {
            throw IllegalArgumentException("Cannot create manifest for empty list of files")
        }

        val s3FileEntries =
            stagedFiles
                .stream()
                .map { file: String ->
                    Entry(getManifestPath(s3Config.bucketName!!, file, stagingPath))
                }
                .collect(Collectors.toList())
        val manifest = Manifest(s3FileEntries)

        return objectMapper.writeValueAsString(manifest)
    }

    private fun putManifest(manifestContents: String, stagingPath: String): String {
        val manifestFilePath = stagingPath + String.format("%s.manifest", UUID.randomUUID())
        s3StorageOperations.uploadManifest(manifestFilePath, manifestContents)
        return manifestFilePath
    }

    private fun executeCopy(
        manifestPath: String,
        destinationHandler: RedshiftDestinationHandler,
        schemaName: String,
        tableName: String,
        suffix: String,
    ) {
        val accessKeyId =
            s3Config.s3CredentialConfig!!.s3CredentialsProvider.credentials.awsAccessKeyId
        val secretAccessKey =
            s3Config.s3CredentialConfig!!.s3CredentialsProvider.credentials.awsSecretKey

        val copyQuery =
            """
            COPY $schemaName.$tableName$suffix FROM '${getFullS3Path(s3Config.bucketName!!, manifestPath)}'
            CREDENTIALS 'aws_access_key_id=$accessKeyId;aws_secret_access_key=$secretAccessKey'
            CSV GZIP
            REGION '${s3Config.bucketRegion}' TIMEFORMAT 'auto'
            STATUPDATE OFF
            MANIFEST;
            """.trimIndent()

        // Disable statement logging. The statement contains a plaintext S3 secret+access key.
        destinationHandler.execute(Sql.of(copyQuery), logStatements = false)
    }

    companion object {
        private val nameTransformer = RedshiftSQLNameTransformer()

        private fun createRawTableQuery(streamId: StreamId, suffix: String): String {
            return """
                CREATE TABLE IF NOT EXISTS "${streamId.rawNamespace}"."${streamId.rawName}$suffix" (
                    ${JavaBaseConstants.COLUMN_NAME_AB_RAW_ID} VARCHAR(36),
                    ${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT} TIMESTAMPTZ DEFAULT GETDATE(),
                    ${JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT} TIMESTAMPTZ,
                    ${JavaBaseConstants.COLUMN_NAME_DATA} SUPER NOT NULL,
                    ${JavaBaseConstants.COLUMN_NAME_AB_META} SUPER NULL,
                    ${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID} BIGINT NULL
                )
            """.trimIndent()
        }

        private fun truncateRawTableQuery(streamId: StreamId, suffix: String): String {
            return """TRUNCATE TABLE "${streamId.rawNamespace}"."${streamId.rawName}$suffix" """
        }

        private fun getFullS3Path(s3BucketName: String, s3StagingFile: String): String {
            return java.lang.String.join("/", "s3:/", s3BucketName, s3StagingFile)
        }

        private fun getManifestPath(
            s3BucketName: String,
            s3StagingFile: String,
            stagingPath: String,
        ): String {
            return "s3://$s3BucketName/$stagingPath$s3StagingFile"
        }
    }
}
