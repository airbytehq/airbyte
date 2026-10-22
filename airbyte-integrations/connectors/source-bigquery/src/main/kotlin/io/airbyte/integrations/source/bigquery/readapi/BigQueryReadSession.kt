/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.google.api.gax.rpc.PermissionDeniedException
import com.google.cloud.bigquery.storage.v1.ArrowSerializationOptions
import com.google.cloud.bigquery.storage.v1.BigQueryReadClient
import com.google.cloud.bigquery.storage.v1.CreateReadSessionRequest
import com.google.cloud.bigquery.storage.v1.DataFormat
import com.google.cloud.bigquery.storage.v1.ReadSession
import com.google.protobuf.Timestamp
import io.airbyte.cdk.ConfigErrorException
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant

private val log = KotlinLogging.logger {}

/**
 * A Storage Read API session on one table: the read streams BigQuery split the table into, in the
 * order the API returned them. That order is the partition order of the connector; the API itself
 * makes no promise about the rows of one read stream relative to another.
 *
 * The session and its read streams live server-side until [expiresAt] (6 hours after creation); any
 * client with the credentials can read a read stream by name from any row offset until then, which
 * is what makes a resumed READ possible.
 */
data class BigQueryReadSession(
    val name: String,
    val expiresAt: Instant,
    /** Resource names of the read streams, index order. */
    val readStreams: List<String>,
    /** The Arrow IPC schema of the rows, when the session was created in this process. */
    val arrowSchema: ByteArray?,
    val estimatedRowCount: Long?,
    val estimatedBytes: Long?,
) {
    override fun toString(): String =
        "BigQueryReadSession(name=$name, expiresAt=$expiresAt, readStreams=${readStreams.size}, " +
            "estimatedRowCount=$estimatedRowCount, estimatedBytes=$estimatedBytes)"

    companion object {
        /** Reads only the table, its type and its metadata; nothing is billed until `ReadRows`. */
        fun create(
            client: BigQueryReadClient,
            jobProjectId: String,
            dataProjectId: String,
            dataset: String,
            table: String,
            selectedFields: List<String>?,
            maxReadStreams: Int,
            arrowBufferCompression: String,
            snapshotTime: Instant? = null,
        ): BigQueryReadSession {
            val readOptions: ReadSession.TableReadOptions.Builder =
                ReadSession.TableReadOptions.newBuilder()
                    .setArrowSerializationOptions(
                        ArrowSerializationOptions.newBuilder()
                            .setBufferCompression(compressionCodec(arrowBufferCompression))
                    )
            selectedFields?.forEach { readOptions.addSelectedFields(it) }
            val session: ReadSession.Builder =
                ReadSession.newBuilder()
                    .setTable("projects/$dataProjectId/datasets/$dataset/tables/$table")
                    .setDataFormat(DataFormat.ARROW)
                    .setReadOptions(readOptions)
            if (snapshotTime != null) {
                session.setTableModifiers(
                    ReadSession.TableModifiers.newBuilder()
                        .setSnapshotTime(
                            Timestamp.newBuilder()
                                .setSeconds(snapshotTime.epochSecond)
                                .setNanos(snapshotTime.nano)
                        )
                )
            }
            val request: CreateReadSessionRequest =
                CreateReadSessionRequest.newBuilder()
                    .setParent("projects/$jobProjectId")
                    .setReadSession(session)
                    .setMaxStreamCount(maxReadStreams)
                    .build()
            val created: ReadSession =
                try {
                    client.createReadSession(request)
                } catch (e: PermissionDeniedException) {
                    throw ConfigErrorException(permissionDeniedMessage(jobProjectId), e)
                }
            val result =
                BigQueryReadSession(
                    name = created.name,
                    expiresAt =
                        Instant.ofEpochSecond(
                            created.expireTime.seconds,
                            created.expireTime.nanos.toLong()
                        ),
                    readStreams = created.streamsList.map { it.name },
                    arrowSchema = created.arrowSchema.serializedSchema.toByteArray(),
                    estimatedRowCount = created.estimatedRowCount.takeIf { it > 0 },
                    estimatedBytes = created.estimatedTotalBytesScanned.takeIf { it > 0 },
                )
            log.info { "Created $result for `$dataProjectId`.`$dataset`.`$table`." }
            return result
        }

        fun compressionCodec(name: String): ArrowSerializationOptions.CompressionCodec =
            when (name.trim().uppercase()) {
                "",
                "NONE",
                "COMPRESSION_UNSPECIFIED" ->
                    ArrowSerializationOptions.CompressionCodec.COMPRESSION_UNSPECIFIED
                "LZ4",
                "LZ4_FRAME" -> ArrowSerializationOptions.CompressionCodec.LZ4_FRAME
                "ZSTD" -> ArrowSerializationOptions.CompressionCodec.ZSTD
                else ->
                    throw IllegalArgumentException(
                        "Unknown Arrow buffer compression '$name'; expected NONE, LZ4_FRAME or ZSTD."
                    )
            }

        /** The message shown when the service account lacks the Read Session User role. */
        fun permissionDeniedMessage(jobProjectId: String): String =
            "The service account is not allowed to use the BigQuery Storage Read API in project " +
                "'$jobProjectId'. Grant it the BigQuery Read Session User role " +
                "(permissions bigquery.readsessions.create and bigquery.readsessions.getData) on " +
                "that project, or disable 'use_storage_read_api' to read through the standard " +
                "query API, which is much slower on large tables."
    }
}
