/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.protocol.models.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import kotlin.io.path.deleteIfExists
import kotlin.io.path.pathString
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericRecord
import org.apache.hadoop.conf.Configuration
import org.apache.parquet.avro.AvroParquetWriter
import org.apache.parquet.hadoop.ParquetWriter
import org.apache.parquet.hadoop.metadata.CompressionCodecName
import org.apache.parquet.io.LocalOutputFile

private val logger = KotlinLogging.logger {}

internal const val PARQUET_FILE_PREFIX = "snowflake"
internal const val PARQUET_FILE_SUFFIX = ".parquet"

class SnowflakeParquetInsertBuffer(
    private val tableName: TableName,
    val columns: LinkedHashMap<String, String>,
    private val snowflakeClient: SnowflakeAirbyteClient,
    val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
) {

    @VisibleForTesting internal var parquetFilePath: Path? = null
    @VisibleForTesting internal var recordCount = 0
    private var writer: ParquetWriter<GenericRecord>? = null
    private var schema: Schema? = null

    private val snowflakeRecordFormatter: SnowflakeRecordFormatter =
        when (snowflakeConfiguration.legacyRawTablesOnly) {
            true -> SnowflakeRawRecordFormatter(columns, snowflakeColumnUtils)
            else -> SnowflakeParquetRecordFormatter(columns, snowflakeColumnUtils)
        }

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (parquetFilePath == null) {
            parquetFilePath =
                Path.of(
                    System.getProperty("java.io.tmpdir"),
                    "$PARQUET_FILE_PREFIX${System.currentTimeMillis()}$PARQUET_FILE_SUFFIX"
                )
            schema = buildSchema()
            writer = buildWriter(schema = schema!!, path = parquetFilePath!!)
        }

        val record = createRecord(recordFields)
        writer?.let { w ->
            w.write(record)
            recordCount++
        }
    }

    suspend fun flush() {
        parquetFilePath?.let { filePath ->
            try {
                writer?.close()
                logger.info { "Beginning insert into ${tableName.toPrettyString(quote = QUOTE)}" }
                // Next, put the CSV file into the staging table
                snowflakeClient.putInStage(tableName, filePath.pathString)
                logger.info {
                    "Copying staging data into ${tableName.toPrettyString(quote = QUOTE)}..."
                }
                // Finally, copy the data from the staging table to the final table
                snowflakeClient.copyFromStage(tableName, filePath.fileName.toString())
                logger.info {
                    "Finished insert of $recordCount row(s) into ${tableName.toPrettyString(quote = QUOTE)}"
                }
            } catch (e: Exception) {
                logger.error(e) { "Unable to flush accumulated data." }
                throw e
            } finally {
                filePath.deleteIfExists()
                writer = null
                recordCount = 0
            }
        }
    }

    private fun buildWriter(schema: Schema, path: Path): ParquetWriter<GenericRecord> =
        AvroParquetWriter.builder<GenericRecord>(LocalOutputFile(path))
            .withSchema(schema)
            .withConf(Configuration())
            .withCompressionCodec(CompressionCodecName.SNAPPY)
            .build()

    private fun buildSchema(): Schema {
        val schema = mutableMapOf<String, Any>()
        schema["type"] = "record"
        schema["name"] = Transformations.toAvroSafeName(tableName.name)
        schema["fields"] =
            columns.map { (key, value) ->
                if (value.equals("VARIANT", true)) {
                    mapOf(
                        "name" to Transformations.toAlphanumericAndUnderscore(key),
                        "type" to
                            mapOf(
                                "type" to snowflakeColumnUtils.toAvroType(value).name,
                                "logicalType" to "variant"
                            ),
                    )
                } else {
                    mapOf(
                        "name" to Transformations.toAlphanumericAndUnderscore(key),
                        "type" to listOf(snowflakeColumnUtils.toAvroType(value).name, "null"),
                    )
                }
            }

        return Schema.Parser().parse(Jsons.serialize(schema))
    }

    private fun createRecord(recordFields: Map<String, AirbyteValue>): GenericRecord {
        val record = GenericData.Record(schema)
        val recordValues = snowflakeRecordFormatter.format(recordFields)
        recordValues.forEachIndexed { index, value ->
            record.put(columns.keys.toList()[index].toSnowflakeCompatibleName(), value)
        }
        return record
    }
}
