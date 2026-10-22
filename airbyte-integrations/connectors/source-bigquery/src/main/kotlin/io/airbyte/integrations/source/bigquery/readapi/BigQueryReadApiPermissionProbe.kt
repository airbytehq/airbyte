/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.google.api.gax.rpc.PermissionDeniedException
import com.google.api.gax.rpc.ServerStream
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.storage.v1.BigQueryReadClient
import com.google.cloud.bigquery.storage.v1.ReadRowsRequest
import com.google.cloud.bigquery.storage.v1.ReadRowsResponse
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigquery.BigQuerySourceConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.grpc.StatusRuntimeException

private val log = KotlinLogging.logger {}

/**
 * Verifies that the service account may use the Storage Read API in the job project, which takes
 * `bigquery.readsessions.create` and `bigquery.readsessions.getData` (the BigQuery Read Session
 * User role) and the API enabled on that project: one read session restricted to a single column
 * and a single read stream, and one `ReadRows` response from it. Nothing but that first response is
 * billed.
 *
 * The session is opened on the table the caller names when it knows a base table (READ: the first
 * one of the catalog), otherwise on the anonymous result table of a `SELECT 1` query job run in the
 * job project. That table always exists, the service account owns it, and it is the kind of table
 * the JDBC driver reads through the Read API when `EnableHighThroughputAPI` is on, so the probe
 * covers the driver's use of the API too. CHECK, which has no catalog, always probes that way; READ
 * does so when the catalog holds only views, which the connector reads through the driver (that
 * case failed a sync before this probe existed: the driver was the first to open a read session,
 * and nothing caught its `PERMISSION_DENIED`).
 *
 * Every failed [Outcome] carries a message meant for the user: what is wrong, and that granting a
 * role, enabling the API or turning `use_storage_read_api` off fixes it. CHECK fails on any of
 * them. READ falls back to the query API on [Outcome.Denied] and keeps the API enabled on
 * [Outcome.Inconclusive], so that a transient error does not silently slow a sync down.
 */
open class BigQueryReadApiPermissionProbe(
    private val config: BigQuerySourceConfiguration,
    private val bigquery: () -> BigQuery,
    private val readClient: () -> BigQueryReadClient,
    private val constants: BigQueryReadApiConstants,
) {
    sealed interface Outcome {
        /** A read session was opened and read on [table]. */
        data class Allowed(val table: TableId) : Outcome

        /**
         * BigQuery refused the request: the role is missing, the API is disabled on the project, or
         * another `PERMISSION_DENIED`. [message] tells the user which, and what to do.
         */
        data class Denied(val message: String, val cause: Throwable) : Outcome

        /**
         * The probe failed for a reason that says nothing about the permission (the API was
         * unreachable, the probe query job failed, ...). [message] says what failed.
         */
        data class Inconclusive(val message: String, val cause: Throwable) : Outcome
    }

    /** The `client_email` of the service account key, for the messages. */
    private val serviceAccount: String? by lazy {
        runCatching { Jsons.readTree(config.credentialsJson)["client_email"]?.asText() }
            .getOrNull()
            ?.takeIf { it.isNotBlank() }
    }

    private val subject: String
        get() = serviceAccount?.let { "The service account $it" } ?: "The service account"

    /**
     * Probes on [table], restricted to [column] when given, or on the result table of a query job
     * when [table] is null.
     */
    open fun probe(table: TableId? = null, column: String? = null): Outcome {
        val target: TableId
        val selectedFields: List<String>?
        if (table != null) {
            target = table
            selectedFields = column?.let { listOf(it) }
        } else {
            target =
                try {
                    queryResultTable()
                } catch (e: Exception) {
                    return Outcome.Inconclusive(
                        "Could not verify that ${subject.replaceFirstChar { it.lowercase() }} " +
                            "may use the BigQuery Storage Read API in project " +
                            "'${config.jobProjectId}': the query job whose result the probe " +
                            "reads failed: ${e.message}",
                        e,
                    )
                }
            selectedFields = listOf(PROBE_COLUMN)
        }
        log.info {
            "Probing the Storage Read API in project '${config.jobProjectId}' on " +
                target.qualifiedName()
        }
        return try {
            val session: BigQueryReadSession =
                BigQueryReadSession.create(
                    client = readClient(),
                    jobProjectId = config.jobProjectId,
                    dataProjectId = target.project,
                    dataset = target.dataset,
                    table = target.table,
                    selectedFields = selectedFields,
                    maxReadStreams = 1,
                    arrowBufferCompression = "NONE",
                )
            session.readStreams.firstOrNull()?.let { readStream: String ->
                readFirstResponse(readStream)
            }
            Outcome.Allowed(target)
        } catch (e: Exception) {
            val denied: PermissionDeniedException? =
                generateSequence(e as Throwable) { it.cause }
                    .filterIsInstance<PermissionDeniedException>()
                    .firstOrNull()
            if (denied == null) {
                Outcome.Inconclusive(
                    "Could not verify that ${subject.replaceFirstChar { it.lowercase() }} " +
                        "may use the BigQuery Storage Read API in project " +
                        "'${config.jobProjectId}': the probe on ${target.qualifiedName()} failed: " +
                        "${e.message}",
                    e,
                )
            } else {
                Outcome.Denied(deniedMessage(denied), e)
            }
        }
    }

    /** Exercises `bigquery.readsessions.getData`: the first `ReadRows` response, then cancel. */
    private fun readFirstResponse(readStream: String) {
        val responses: ServerStream<ReadRowsResponse> =
            readClient()
                .readRowsCallable()
                .call(
                    ReadRowsRequest.newBuilder().setReadStream(readStream).setOffset(0L).build(),
                    BigQueryReadApiPartitionReader.callContext(constants),
                )
        try {
            val iterator: Iterator<ReadRowsResponse> = responses.iterator()
            if (iterator.hasNext()) iterator.next()
        } finally {
            responses.cancel()
        }
    }

    /**
     * What is wrong and what to do about it, in the user's terms: the missing role (the common
     * case, recognized by the permission BigQuery names), the API disabled on the project, or
     * whatever else BigQuery said.
     */
    private fun deniedMessage(denied: PermissionDeniedException): String {
        val detail: String =
            generateSequence(denied as Throwable) { it.cause }
                .filterIsInstance<StatusRuntimeException>()
                .firstOrNull()
                ?.status
                ?.description
                ?: denied.message ?: denied.toString()
        val project: String = config.jobProjectId
        val problem: String =
            when {
                detail.contains("bigquery.readsessions.") ->
                    "$subject is not allowed to use the BigQuery Storage Read API in project " +
                        "'$project'. Grant it the BigQuery Read Session User role " +
                        "(roles/bigquery.readSessionUser, which holds " +
                        "bigquery.readsessions.create and bigquery.readsessions.getData) on " +
                        "project '$project'"
                isApiDisabled(denied, detail) ->
                    "The BigQuery Storage Read API is not enabled in project '$project'. Enable " +
                        "the BigQuery Storage API (bigquerystorage.googleapis.com) for that " +
                        "project in the Google Cloud console"
                else ->
                    "BigQuery denied ${subject.replaceFirstChar { it.lowercase() }} the use of " +
                        "the Storage Read API in project '$project'. Check its roles on that " +
                        "project (it needs the BigQuery Read Session User role)"
            }
        return "$problem, or $TURN_OFF_ADVICE. BigQuery said: $detail"
    }

    private fun isApiDisabled(denied: PermissionDeniedException, detail: String): Boolean =
        runCatching { denied.reason }.getOrNull() == "SERVICE_DISABLED" ||
            detail.contains("has not been used in project") ||
            detail.contains("it is disabled")

    /**
     * The anonymous table holding the result of a `SELECT 1` job in the job project. The query
     * processes no bytes; BigQuery keeps the table for 24 hours.
     */
    private fun queryResultTable(): TableId {
        val job: Job =
            bigquery()
                .create(JobInfo.of(QueryJobConfiguration.newBuilder(PROBE_QUERY).build()))
                .waitFor()
                ?: throw IllegalStateException("the job vanished before it completed")
        job.status?.error?.let { error -> throw IllegalStateException(error.message) }
        val configuration: QueryJobConfiguration = job.getConfiguration()
        return configuration.destinationTable
            ?: throw IllegalStateException("BigQuery reported no result table for job ${job.jobId}")
    }

    companion object {
        /** `project.dataset.table`; [TableId.toString] prints the Google API's generic map. */
        fun TableId.qualifiedName(): String =
            listOfNotNull(project, dataset, table).joinToString(".")

        const val PROBE_COLUMN = "probe"
        const val PROBE_QUERY = "SELECT 1 AS $PROBE_COLUMN"

        /** The way out that needs no Google Cloud change; shared by every failure message. */
        const val TURN_OFF_ADVICE: String =
            "turn off 'Use the BigQuery Storage Read API' (use_storage_read_api) in the source " +
                "settings to read through the standard query API, which is much slower on large " +
                "tables"
    }
}
