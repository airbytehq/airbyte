/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.do_stuff_with_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobConfiguration
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TimePartitioning
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.ConnectorExceptionUtil
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.DestinationColumnNameMapping
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.DestinationInitialStatus
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.InitialFinalTableStatus
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.InitialRawTableStatus
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.Sql
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.TableName
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.TableNames
import io.airbyte.integrations.destination.bigquery.util.BigQueryUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.UUID

private val logger = KotlinLogging.logger {}

class BigqueryDestinationHandler(private val bq: BigQuery, private val datasetLocation: String) {
    fun execute(sql: Sql) {
        val transactions = sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION")
        if (transactions.isEmpty()) {
            return
        }
        val queryId = UUID.randomUUID()
        val statement = java.lang.String.join("\n", transactions)
        logger.debug { "Executing sql $queryId}: $statement" }

        /*
         * If you run a query like CREATE SCHEMA ... OPTIONS(location=foo); CREATE TABLE ...;, bigquery
         * doesn't do a good job of inferring the query location. Pass it in explicitly.
         */
        var job =
            bq.create(
                JobInfo.of(
                    JobId.newBuilder().setLocation(datasetLocation).build(),
                    QueryJobConfiguration.newBuilder(statement).build()
                )
            )
        //        AirbyteExceptionHandler.addStringForDeinterpolation(job.etag)
        // job.waitFor() gets stuck forever in some failure cases, so manually poll the job instead.
        while (JobStatus.State.DONE != job.status.state) {
            Thread.sleep(1000L)
            job = job.reload()
        }
        if (job.status.error != null) {
            throw BigQueryException(listOf(job.status.error) + job.status.executionErrors)
        }

        val statistics = job.getStatistics<JobStatistics.QueryStatistics>()
        logger.debug {
            "Root-level job $queryId completed in ${statistics.endTime - statistics.startTime} ms; processed ${statistics.totalBytesProcessed} bytes; billed for ${statistics.totalBytesBilled} bytes"
        }

        // SQL transactions can spawn child jobs, which are billed individually. Log their stats
        // too.
        if (statistics.numChildJobs != null) {
            // There isn't (afaict) anything resembling job.getChildJobs(), so we have to ask bq for
            // them
            bq.listJobs(BigQuery.JobListOption.parentJobId(job.jobId.job))
                .streamAll()
                .sorted(
                    Comparator.comparing { childJob: Job ->
                        childJob.getStatistics<JobStatistics>().endTime
                    }
                )
                .forEach { childJob: Job ->
                    val configuration = childJob.getConfiguration<JobConfiguration>()
                    if (configuration is QueryJobConfiguration) {
                        val childQueryStats =
                            childJob.getStatistics<JobStatistics.QueryStatistics>()
                        var truncatedQuery: String =
                            configuration.query
                                .replace("\n".toRegex(), " ")
                                .replace(" +".toRegex(), " ")
                                .substring(0, 100.coerceAtMost(configuration.query.length))
                        if (truncatedQuery != configuration.query) {
                            truncatedQuery += "..."
                        }
                        logger.debug {
                            "Child sql $truncatedQuery completed in ${childQueryStats.endTime - childQueryStats.startTime} ms; processed ${childQueryStats.totalBytesProcessed} bytes; billed for ${childQueryStats.totalBytesBilled} bytes"
                        }
                    } else {
                        // other job types are extract/copy/load
                        // we're probably not using them, but handle just in case?
                        val childJobStats = childJob.getStatistics<JobStatistics>()
                        logger.debug {
                            "Non-query child job (${configuration.type}) completed in ${childJobStats.endTime - childJobStats.startTime} ms"
                        }
                    }
                }
        }
    }

    fun createNamespaces(schemas: Set<String>) {
        schemas.forEach { dataset: String -> createDataset(dataset) }
    }

    // TODO ... why is this not just done in BigQueryUtils?
    //   and/or can we kill BigQueryUtils.getOrCreateDataset?
    private fun createDataset(dataset: String) {
        logger.info { "Creating dataset if not present $dataset" }
        try {
            BigQueryUtils.getOrCreateDataset(bq, dataset, datasetLocation)
        } catch (e: BigQueryException) {
            if (ConnectorExceptionUtil.HTTP_AUTHENTICATION_ERROR_CODES.contains(e.code)) {
                throw ConfigErrorException(e.message!!, e)
            } else {
                throw e
            }
        }
    }

    fun gatherInitialState(
        streams: List<Triple<DestinationStream, TableNames, DestinationColumnNameMapping>>
    ): List<DestinationInitialStatus<Unit>> {
        return streams.map { (stream, tableNames, destinationColumnMapping) ->
            gatherInitialState(stream, tableNames, destinationColumnMapping)
        }
    }

    private fun gatherInitialState(
        stream: DestinationStream,
        tableNames: TableNames,
        destinationColumnNameMapping: DestinationColumnNameMapping,
    ): DestinationInitialStatus<Unit> {
        val finalTable = findExistingTable(tableNames.finalTableName!!)
        val rawTableState = getInitialRawTableState(tableNames.oldStyleRawTableName!!, suffix = "")
        val tempRawTableState =
            getInitialRawTableState(
                tableNames.oldStyleRawTableName,
                suffix = TableNames.TMP_TABLE_SUFFIX
            )
        return DestinationInitialStatus(
            stream,
            rawTableState,
            tempRawTableState,
            InitialFinalTableStatus(
                // for now, just use 0. this means we will always use a temp final table.
                // platform has a workaround for this, so it's OK.
                // TODO only fetch this on truncate syncs
                // TODO once we have destination state, use that instead of a query
                generationId = 0,
                schemaMismatch =
                    finalTable != null &&
                        !existingSchemaMatchesStreamConfig(
                            stream,
                            destinationColumnNameMapping,
                            finalTable
                        ),
            ),
            // temp table is always empty until we commit, so always return null
            tempFinalTableGenerationId = null,
            // we don't have actual destination state, just use Unit
            destinationState = Unit,
        )
    }

    private fun findExistingTable(tableName: TableName): TableDefinition? {
        return bq.getTable(tableName.namespace, tableName.name)?.getDefinition()
    }

    private fun getInitialRawTableState(id: TableName, suffix: String): InitialRawTableStatus? {
        bq.getTable(TableId.of(id.namespace, id.name + suffix))
            ?: // Table doesn't exist. There are no unprocessed records, and no timestamp.
        return null

        val rawTableId =
            """${BigquerySqlGenerator.quote(id.namespace)}.${BigquerySqlGenerator.quote(id.name)}"""
        val unloadedRecordTimestamp =
            bq.query(
                    QueryJobConfiguration.newBuilder(
                            // bigquery timestamps have microsecond precision
                            """
                    SELECT TIMESTAMP_SUB(MIN(_airbyte_extracted_at), INTERVAL 1 MICROSECOND)
                    FROM $rawTableId
                    WHERE _airbyte_loaded_at IS NULL
                    """.trimIndent()
                        )
                        .build()
                )
                .iterateAll()
                .iterator()
                .next()
                .first()
        // If this value is null, then there are no records with null loaded_at.
        // If it's not null, then we can return immediately - we've found some unprocessed records
        // and their
        // timestamp.
        if (!unloadedRecordTimestamp.isNull) {
            return InitialRawTableStatus(
                true,
                maxProcessedTimestamp = unloadedRecordTimestamp.timestampInstant,
            )
        }

        val loadedRecordTimestamp =
            bq.query(
                    QueryJobConfiguration.newBuilder(
                            """
                    SELECT MAX(_airbyte_extracted_at)
                    FROM $rawTableId
                    """.trimIndent()
                        )
                        .build()
                )
                .iterateAll()
                .iterator()
                .next()
                .first()
        // We know (from the previous query) that all records have been processed by T+D already.
        // So we just need to get the timestamp of the most recent record.
        return if (loadedRecordTimestamp.isNull) {
            // Null timestamp because the table is empty. T+D can process the entire raw table
            // during this sync.
            InitialRawTableStatus(false, maxProcessedTimestamp = null)
        } else {
            // The raw table already has some records. T+D can skip all records with timestamp <=
            // this value.
            InitialRawTableStatus(
                false,
                maxProcessedTimestamp = loadedRecordTimestamp.timestampInstant,
            )
        }
    }

    private fun existingSchemaMatchesStreamConfig(
        stream: DestinationStream,
        destinationColumnNameMapping: DestinationColumnNameMapping,
        existingTable: TableDefinition
    ): Boolean {
        val alterTableReport =
            buildAlterTableReport(stream, destinationColumnNameMapping, existingTable)
        var tableClusteringMatches = false
        var tablePartitioningMatches = false
        if (existingTable is StandardTableDefinition) {
            tableClusteringMatches =
                clusteringMatches(stream, destinationColumnNameMapping, existingTable)
            tablePartitioningMatches = partitioningMatches(existingTable)
        }
        logger.info {
            "Alter Table Report ${alterTableReport.columnsToAdd} ${alterTableReport.columnsToRemove} ${alterTableReport.columnsToChangeType}; Clustering $tableClusteringMatches; Partitioning $tablePartitioningMatches"
        }
        return alterTableReport.isNoOp && tableClusteringMatches && tablePartitioningMatches
    }

    private fun buildAlterTableReport(
        stream: DestinationStream,
        destinationColumnNameMapping: DestinationColumnNameMapping,
        existingTable: TableDefinition
    ): AlterTableReport {
        val pks: List<String> =
            when (stream.importType) {
                Append,
                Overwrite -> emptyList()
                is Dedupe ->
                    (stream.importType as Dedupe).primaryKey.map {
                        destinationColumnNameMapping[it.first()]!!
                    }
            }

        val streamSchema: Map<String, StandardSQLTypeName> =
            (stream.schema as ObjectType).properties.mapValues { (_, type) ->
                BigquerySqlGenerator.toDialectType(type.type)
            }

        val existingSchema: Map<String, StandardSQLTypeName> =
            existingTable.schema!!.fields.associate { it.name to it.type.standardType }

        // Columns in the StreamConfig that don't exist in the TableDefinition
        val columnsToAdd: Set<String> =
            streamSchema.keys
                .filter { name -> !existingSchema.keys.containsIgnoreCase(name) }
                .toSet()

        // Columns in the current schema that are no longer in the StreamConfig
        val columnsToRemove =
            existingSchema.keys
                .filter { name: String ->
                    !streamSchema.keys.containsIgnoreCase(name) &&
                        // TODO we have this list somewhere, just need to find it
                        !JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.containsIgnoreCase(name)
                }
                .toSet()

        // TODO super rough port from java Streams API to kotlin collection processing,
        //   needs some cleanup
        // Columns that are typed differently than the StreamConfig
        val columnsToChangeType =
            (streamSchema.keys
                    // If it's not in the existing schema, it should already be in the
                    // columnsToAdd Set
                    .filter { name: String ->
                        existingSchema.keys
                            .matchingKey(name)
                            // if it does exist, only include it in this set if the type (the
                            // value in each respective map)
                            // is different between the stream and existing schemas
                            ?.let { existingSchema[it] != streamSchema[name] }
                        // if there is no matching key, then don't include it because it
                        // is probably already in columnsToAdd
                        ?: false
                    } +
                    // OR columns that used to have a non-null constraint and shouldn't
                    // (https://github.com/airbytehq/airbyte/pull/31082)
                    existingTable.schema!!
                        .fields
                        .filter { field -> pks.contains(field.name) }
                        .filter { field -> field.mode == Field.Mode.REQUIRED }
                        .map { obj: Field -> obj.name })
                .toSet()

        return AlterTableReport(
            columnsToAdd,
            columnsToRemove,
            columnsToChangeType,
        )
    }

    private fun clusteringMatches(
        stream: DestinationStream,
        destinationColumnNameMapping: DestinationColumnNameMapping,
        existingTable: StandardTableDefinition
    ): Boolean {
        return existingTable.clustering != null &&
            BigquerySqlGenerator.clusteringColumns(stream, destinationColumnNameMapping).all {
                expectedClusteringColumn ->
                existingTable.clustering!!.fields.any {
                    it.equals(expectedClusteringColumn, ignoreCase = true)
                }
            }
    }

    private fun partitioningMatches(existingTable: StandardTableDefinition): Boolean {
        return existingTable.timePartitioning != null &&
            existingTable.timePartitioning!!
                .field
                .equals("_airbyte_extracted_at", ignoreCase = true) &&
            TimePartitioning.Type.DAY == existingTable.timePartitioning!!.type
    }
}

data class AlterTableReport(
    val columnsToAdd: Set<String>,
    val columnsToRemove: Set<String>,
    val columnsToChangeType: Set<String>,
) {
    val isNoOp =
        this.columnsToAdd.isEmpty() && columnsToRemove.isEmpty() && columnsToChangeType.isEmpty()
}

fun Collection<String>.containsIgnoreCase(target: String): Boolean =
    this.any { it.equals(target, ignoreCase = true) }

fun Collection<String>.matchingKey(target: String): String? =
    this.firstOrNull { it.equals(target, ignoreCase = true) }
