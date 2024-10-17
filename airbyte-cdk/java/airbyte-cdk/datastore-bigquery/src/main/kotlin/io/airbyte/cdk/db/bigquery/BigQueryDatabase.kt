/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.google.api.gax.retrying.RetrySettings
import com.google.auth.oauth2.ServiceAccountCredentials
import com.google.cloud.bigquery.*
import com.google.common.base.Charsets
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Streams
import io.airbyte.cdk.db.SqlDatabase
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.IOException
import java.sql.SQLException
import java.util.*
import java.util.function.Consumer
import java.util.stream.Stream
import org.apache.commons.lang3.StringUtils
import org.apache.commons.lang3.tuple.ImmutablePair
import org.threeten.bp.Duration

private val LOGGER = KotlinLogging.logger {}

class BigQueryDatabase
@JvmOverloads
constructor(
    projectId: String?,
    jsonCreds: String?,
    sourceOperations: BigQuerySourceOperations? = BigQuerySourceOperations()
) : SqlDatabase() {
    var bigQuery: BigQuery
    private var sourceOperations: BigQuerySourceOperations? = null

    init {
        try {
            this.sourceOperations = sourceOperations
            val bigQueryBuilder = BigQueryOptions.newBuilder()
            var credentials: ServiceAccountCredentials? = null
            if (jsonCreds != null && !jsonCreds.isEmpty()) {
                credentials =
                    ServiceAccountCredentials.fromStream(
                        ByteArrayInputStream(jsonCreds.toByteArray(Charsets.UTF_8))
                    )
            }
            bigQuery =
                bigQueryBuilder
                    .setProjectId(projectId)
                    .setCredentials(
                        if (!Objects.isNull(credentials)) credentials
                        else ServiceAccountCredentials.getApplicationDefault()
                    )
                    .setHeaderProvider {
                        ImmutableMap.of("user-agent", getUserAgentHeader(connectorVersion))
                    }
                    .setRetrySettings(
                        RetrySettings.newBuilder()
                            .setMaxAttempts(10)
                            .setRetryDelayMultiplier(1.5)
                            .setTotalTimeout(Duration.ofMinutes(60))
                            .build()
                    )
                    .build()
                    .service
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    private fun getUserAgentHeader(connectorVersion: String): String {
        return String.format(AGENT_TEMPLATE, connectorVersion)
    }

    private val connectorVersion: String
        get() =
            Optional.ofNullable(System.getenv("WORKER_CONNECTOR_IMAGE"))
                .orElse(StringUtils.EMPTY)
                .replace("airbyte/", StringUtils.EMPTY)
                .replace(":", "/")

    @Throws(SQLException::class)
    override fun execute(sql: String?) {
        val result = executeQuery(bigQuery, getQueryConfig(sql, emptyList()))
        if (result.getLeft() == null) {
            throw SQLException(
                "BigQuery request is failed with error: ${result.getRight()}. SQL: ${sql}"
            )
        }
        LOGGER.info { "BigQuery successfully finished execution SQL: $sql" }
    }

    @Throws(Exception::class)
    fun query(sql: String?, vararg params: QueryParameterValue): Stream<JsonNode> {
        return query(sql, listOf(*params))
    }

    @Throws(Exception::class)
    override fun unsafeQuery(sql: String?, vararg params: String): Stream<JsonNode> {
        val parameterValueList =
            params.map { param: String ->
                QueryParameterValue.newBuilder()
                    .setValue(param)
                    .setType(StandardSQLTypeName.STRING)
                    .build()
            }

        return query(sql, parameterValueList)
    }

    @JvmOverloads
    @Throws(Exception::class)
    fun query(sql: String?, params: List<QueryParameterValue>? = emptyList()): Stream<JsonNode> {
        val result = executeQuery(bigQuery, getQueryConfig(sql, params))

        if (result.getLeft() != null) {
            val fieldList = result.getLeft()!!.getQueryResults().schema!!.fields
            return Streams.stream(result.getLeft()!!.getQueryResults().iterateAll()).map {
                fieldValues: FieldValueList ->
                sourceOperations!!.rowToJson(BigQueryResultSet(fieldValues, fieldList))
            }
        } else
            throw Exception(
                "Failed to execute query " +
                    sql +
                    (if (params != null && !params.isEmpty()) " with params $params" else "") +
                    ". Error: " +
                    result.getRight()
            )
    }

    fun getQueryConfig(sql: String?, params: List<QueryParameterValue>?): QueryJobConfiguration {
        return QueryJobConfiguration.newBuilder(sql)
            .setUseLegacySql(false)
            .setPositionalParameters(params)
            .build()
    }

    fun executeQuery(
        bigquery: BigQuery,
        queryConfig: QueryJobConfiguration?
    ): ImmutablePair<Job?, String?> {
        val jobId = JobId.of(UUID.randomUUID().toString())
        val queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build())
        return executeQuery(queryJob)
    }

    /**
     * Returns full information about all tables from entire project
     *
     * @param projectId BigQuery project id
     * @return List of BigQuery tables
     */
    fun getProjectTables(projectId: String?): List<Table> {
        val tableList: MutableList<Table> = ArrayList()
        bigQuery
            .listDatasets(projectId)
            .iterateAll()
            .forEach(
                Consumer { dataset: Dataset ->
                    bigQuery
                        .listTables(dataset.datasetId)
                        .iterateAll()
                        .forEach(
                            Consumer { table: Table ->
                                tableList.add(bigQuery.getTable(table.tableId))
                            }
                        )
                }
            )
        return tableList
    }

    /**
     * Returns full information about all tables from specific Dataset
     *
     * @param datasetId BigQuery dataset id
     * @return List of BigQuery tables
     */
    fun getDatasetTables(datasetId: String?): List<Table> {
        val tableList: MutableList<Table> = ArrayList()
        bigQuery
            .listTables(datasetId)
            .iterateAll()
            .forEach(Consumer { table: Table -> tableList.add(bigQuery.getTable(table.tableId)) })
        return tableList
    }

    fun cleanDataSet(dataSetId: String) {
        // allows deletion of a dataset that has contents
        val option = BigQuery.DatasetDeleteOption.deleteContents()

        val success = bigQuery.delete(dataSetId, option)
        if (success) {
            LOGGER.info { "BQ Dataset $dataSetId deleted..." }
        } else {
            LOGGER.info { "BQ Dataset cleanup for $dataSetId failed!" }
        }
    }

    private fun executeQuery(queryJob: Job): ImmutablePair<Job?, String?> {
        val completedJob = waitForQuery(queryJob)
        if (completedJob.status.error != null) {
            // You can also look at queryJob.getStatus().getExecutionErrors() for all
            // errors, not just the latest one.
            return ImmutablePair.of(null, (completedJob.status.error.toString()))
        }

        return ImmutablePair.of(completedJob, null)
    }

    private fun waitForQuery(queryJob: Job): Job {
        try {
            return queryJob.waitFor()
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
    }

    companion object {

        private const val AGENT_TEMPLATE = "%s (GPN: Airbyte; staging)"
    }
}
