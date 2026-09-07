/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.sql.PreparedStatement
import java.sql.Timestamp
import java.sql.Types
import java.time.Clock
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

private const val FLUSH_LIMIT = 1000

/**
 * Accumulates and flushes records to Redshift via batched INSERT statements. NOT a @Singleton -
 * created per-stream by AggregateFactory.
 *
 * Uses JDBC batch operations to efficiently insert multiple records in a single database
 * round-trip, avoiding connection pool exhaustion.
 */
class RedshiftAggregate(
    private val tableName: TableName,
    private val dataSource: DataSource,
) : Aggregate {

    private val buffer = mutableListOf<Map<String, AirbyteValue>>()

    override fun accept(record: RecordDTO) {
        buffer.add(record.fields)
        if (buffer.size >= FLUSH_LIMIT) {
            kotlinx.coroutines.runBlocking { flush() }
        }
    }

    override suspend fun flush() {
        if (buffer.isEmpty()) return

        try {
            log.info { "Flushing ${buffer.size} records to $tableName..." }
            insertBatch(buffer)
            log.info { "Finished flushing ${buffer.size} records" }
        } finally {
            buffer.clear()
        }
    }

    private fun insertBatch(records: List<Map<String, AirbyteValue>>) {
        if (records.isEmpty()) return

        // All records should have the same schema, use first record for column names
        val firstRecord = records.first()
        val columns = firstRecord.keys.joinToString(", ") { "\"$it\"" }
        val placeholders = firstRecord.keys.joinToString(", ") { "?" }
        val sql =
            """
            INSERT INTO "${tableName.namespace}"."${tableName.name}" ($columns)
            VALUES ($placeholders)
        """.trimIndent()

        dataSource.connection.use { connection ->
            connection.prepareStatement(sql).use { statement ->
                for (record in records) {
                    record.values.forEachIndexed { index, value ->
                        setParameter(statement, index + 1, value)
                    }
                    statement.addBatch()
                }
                statement.executeBatch()
            }
        }
    }

    private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
        when (value) {
            is NullValue -> statement.setNull(index, Types.VARCHAR)
            is StringValue -> statement.setString(index, value.value.replace("\u0000", " "))
            is IntegerValue -> statement.setLong(index, value.value.toLong())
            is NumberValue -> statement.setDouble(index, value.value.toDouble())
            is BooleanValue -> statement.setBoolean(index, value.value)
            is DateValue -> statement.setDate(index, java.sql.Date.valueOf(value.value))
            is TimeWithTimezoneValue -> statement.setString(index, value.value.toString())
            is TimeWithoutTimezoneValue -> statement.setString(index, value.value.toString())
            is TimestampWithTimezoneValue ->
                statement.setTimestamp(index, Timestamp.from(value.value.toInstant()))
            is TimestampWithoutTimezoneValue ->
                statement.setTimestamp(index, Timestamp.valueOf(value.value))
            is ObjectValue -> statement.setString(index, value.values.serializeToString())
            is ArrayValue -> statement.setString(index, value.values.serializeToString())
        }
    }
}

@Factory
class RedshiftAggregateFactory(
    private val dataSource: DataSource,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val config: RedshiftV2Configuration,
    private val clock: Clock,
    private val catalog: DestinationCatalog,
) : AggregateFactory {

    @Singleton
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val stream = catalog.getStream(key)
        val finalSchema: Map<String, ColumnType> = stream.tableSchema.columnSchema.finalSchema

        // Use staging aggregate if S3 config is present, otherwise use direct inserts
        return if (config.s3Config != null) {
            log.info { "Using S3 staging for stream: $tableName" }
            RedshiftStagingAggregate(tableName, dataSource, config.s3Config, clock, finalSchema)
        } else {
            log.info { "Using direct inserts for stream: $tableName" }
            RedshiftAggregate(tableName, dataSource)
        }
    }
}
