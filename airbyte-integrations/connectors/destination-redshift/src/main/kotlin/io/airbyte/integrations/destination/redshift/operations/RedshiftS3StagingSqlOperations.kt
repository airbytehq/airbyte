/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.operations

import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.ObjectMapper
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryption
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryptionBlobDecorator
import io.airbyte.cdk.integrations.destination.s3.EncryptionConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.staging.StagingOperations
import io.airbyte.commons.lang.Exceptions.toRuntime
import io.airbyte.integrations.destination.redshift.manifest.Entry
import io.airbyte.integrations.destination.redshift.manifest.Manifest
import java.time.Instant
import java.time.ZoneOffset
import java.util.*
import java.util.stream.Collectors
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
class RedshiftS3StagingSqlOperations(
    private val nameTransformer: NamingConventionTransformer,
    s3Client: AmazonS3?,
    private val s3Config: S3DestinationConfig,
    encryptionConfig: EncryptionConfig
) : RedshiftSqlOperations(), StagingOperations {
    private val s3StorageOperations = S3StorageOperations(nameTransformer, s3Client!!, s3Config)
    private val objectMapper = ObjectMapper()
    private val keyEncryptingKey: ByteArray?

    init {
        if (encryptionConfig is AesCbcEnvelopeEncryption) {
            s3StorageOperations.addBlobDecorator(
                AesCbcEnvelopeEncryptionBlobDecorator(encryptionConfig.key)
            )
            this.keyEncryptingKey = encryptionConfig.key
        } else {
            this.keyEncryptingKey = null
        }
    }

    override fun getStagingPath(
        connectionId: UUID?,
        namespace: String?,
        streamName: String?,
        outputTableName: String?,
        writeDatetime: Instant?
    ): String? {
        val bucketPath = s3Config.bucketPath
        val prefix =
            if (bucketPath!!.isEmpty()) ""
            else bucketPath + (if (bucketPath.endsWith("/")) "" else "/")
        val zdt = writeDatetime!!.atZone(ZoneOffset.UTC)
        return nameTransformer.applyDefaultCase(
            String.format(
                "%s%s/%s_%02d_%02d_%02d_%s/",
                prefix,
                nameTransformer.applyDefaultCase(
                    nameTransformer.convertStreamName(outputTableName!!)
                ),
                zdt.year,
                zdt.monthValue,
                zdt.dayOfMonth,
                zdt.hour,
                connectionId
            )
        )
    }

    override fun getStageName(namespace: String?, streamName: String?): String? {
        return "garbage-unused"
    }

    @Throws(Exception::class)
    override fun createStageIfNotExists(database: JdbcDatabase?, stageName: String?) {
        s3StorageOperations.createBucketIfNotExists()
    }

    @Throws(Exception::class)
    override fun uploadRecordsToStage(
        database: JdbcDatabase?,
        recordsData: SerializableBuffer?,
        schemaName: String?,
        stageName: String?,
        stagingPath: String?
    ): String {
        return s3StorageOperations.uploadRecordsToBucket(recordsData!!, schemaName, stagingPath!!)
    }

    private fun putManifest(manifestContents: String, stagingPath: String?): String {
        val manifestFilePath = stagingPath + String.format("%s.manifest", UUID.randomUUID())
        s3StorageOperations.uploadManifest(manifestFilePath, manifestContents)
        return manifestFilePath
    }

    @Throws(Exception::class)
    override fun copyIntoTableFromStage(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?,
        stagedFiles: List<String>?,
        tableName: String?,
        schemaName: String?
    ) {
        LOGGER.info(
            "Starting copy to target table from stage: {} in destination from stage: {}, schema: {}, .",
            tableName,
            stagingPath,
            schemaName
        )
        val possibleManifest = Optional.ofNullable(createManifest(stagedFiles, stagingPath))
        toRuntime {
            possibleManifest
                .stream()
                .map { manifestContent: String -> putManifest(manifestContent, stagingPath) }
                .forEach { manifestPath: String ->
                    executeCopy(manifestPath, database, schemaName, tableName)
                }
        }
        LOGGER.info("Copy to target table {}.{} in destination complete.", schemaName, tableName)
    }

    /** Generates the COPY data from staging files into target table */
    private fun executeCopy(
        manifestPath: String,
        db: JdbcDatabase?,
        schemaName: String?,
        tableName: String?
    ) {
        val credentialConfig = s3Config.s3CredentialConfig as S3AccessKeyCredentialConfig?
        val encryptionClause =
            if (keyEncryptingKey == null) {
                ""
            } else {
                String.format(
                    " encryption = (type = 'aws_cse' master_key = '%s')",
                    BASE64_ENCODER.encodeToString(keyEncryptingKey)
                )
            }

        val copyQuery =
            String.format(
                """
        COPY %s.%s FROM '%s'
        CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
        %s
        CSV GZIP
        REGION '%s' TIMEFORMAT 'auto'
        STATUPDATE OFF
        MANIFEST;
        """.trimIndent(),
                schemaName,
                tableName,
                getFullS3Path(s3Config.bucketName, manifestPath),
                credentialConfig!!.accessKeyId,
                credentialConfig.secretAccessKey,
                encryptionClause,
                s3Config.bucketRegion
            )

        toRuntime { db!!.execute(copyQuery) }
    }

    private fun createManifest(stagedFiles: List<String?>?, stagingPath: String?): String? {
        if (stagedFiles!!.isEmpty()) {
            return null
        }

        val s3FileEntries =
            stagedFiles
                .stream()
                .map { file: String? ->
                    Entry(getManifestPath(s3Config.bucketName, file!!, stagingPath))
                }
                .collect(Collectors.toList())
        val manifest = Manifest(s3FileEntries)

        return toRuntime<String> { objectMapper.writeValueAsString(manifest) }
    }

    @Throws(Exception::class)
    override fun dropStageIfExists(
        database: JdbcDatabase?,
        stageName: String?,
        stagingPath: String?
    ) {
        // stageName is unused here but used in Snowflake. This interface needs to be fixed.
        s3StorageOperations.dropBucketObject(stagingPath!!)
    }

    companion object {
        private val BASE64_ENCODER: Base64.Encoder = Base64.getEncoder()
        private val LOGGER: Logger =
            LoggerFactory.getLogger(RedshiftS3StagingSqlOperations::class.java)

        private fun getFullS3Path(s3BucketName: String?, s3StagingFile: String): String {
            return java.lang.String.join("/", "s3:/", s3BucketName, s3StagingFile)
        }

        private fun getManifestPath(
            s3BucketName: String?,
            s3StagingFile: String,
            stagingPath: String?
        ): String {
            return "s3://$s3BucketName/$stagingPath$s3StagingFile"
        }
    }
}
