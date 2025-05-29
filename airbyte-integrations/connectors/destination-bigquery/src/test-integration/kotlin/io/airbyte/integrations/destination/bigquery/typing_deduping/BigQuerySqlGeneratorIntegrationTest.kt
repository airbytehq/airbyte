/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.*
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.deserializeExact
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.integrations.base.destination.typing_deduping.*
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.BigQueryDestination.Companion.getBigQuery
import io.airbyte.integrations.destination.bigquery.migrators.BigQueryDestinationState
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import java.util.*
import java.util.Map
import java.util.stream.Collectors
import kotlin.collections.LinkedHashMap
import kotlin.collections.List
import kotlin.collections.emptyList
import kotlin.collections.indices
import org.apache.commons.text.StringSubstitutor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@Execution(ExecutionMode.CONCURRENT)
class BigQuerySqlGeneratorIntegrationTest :
    BaseSqlGeneratorIntegrationTest<BigQueryDestinationState>() {
    override val sqlGenerator: BigQuerySqlGenerator
        get() = BigQuerySqlGenerator(projectId, datasetLocation)

    override val destinationHandler: BigQueryDestinationHandler
        get() = BigQueryDestinationHandler(bq!!, "US")

    override fun createNamespace(namespace: String) {
        bq!!.create(
            DatasetInfo.newBuilder(
                    namespace
                ) // This unfortunately doesn't delete the actual dataset after 3 days, but at least
                // we'll clear out
                // old tables automatically
                .setDefaultTableLifetime(Duration.ofDays(3).toMillis())
                .build()
        )
    }

    @Throws(InterruptedException::class)
    override fun createRawTable(streamId: StreamId) {
        bq!!.query(
            QueryJobConfiguration.newBuilder(
                    StringSubstitutor(
                            Map.of("raw_table_id", streamId.rawTableId(BigQuerySqlGenerator.QUOTE))
                        )
                        .replace(
                            """
                CREATE TABLE ${'$'}{raw_table_id} (
                  _airbyte_raw_id STRING NOT NULL,
                  _airbyte_data STRING NOT NULL,
                  _airbyte_extracted_at TIMESTAMP NOT NULL,
                  _airbyte_loaded_at TIMESTAMP,
                  _airbyte_meta STRING,
                  _airbyte_generation_id INTEGER
                ) PARTITION BY (
                  DATE_TRUNC(_airbyte_extracted_at, DAY)
                ) CLUSTER BY _airbyte_loaded_at;
                
                """.trimIndent()
                        )
                )
                .build()
        )
    }

    @Throws(Exception::class)
    override fun createV1RawTable(v1RawTable: StreamId) {
        bq!!.query(
            QueryJobConfiguration.newBuilder(
                    StringSubstitutor(
                            Map.of(
                                "raw_table_id",
                                v1RawTable.rawTableId(BigQuerySqlGenerator.QUOTE)
                            )
                        )
                        .replace(
                            """
                        CREATE TABLE ${'$'}{raw_table_id} (
                          _airbyte_ab_id STRING NOT NULL,
                          _airbyte_data STRING NOT NULL,
                          _airbyte_emitted_at TIMESTAMP NOT NULL,
                        ) PARTITION BY (
                          DATE_TRUNC(_airbyte_emitted_at, DAY)
                        ) CLUSTER BY _airbyte_emitted_at;
                        
                        """.trimIndent()
                        )
                )
                .build()
        )
    }

    @Throws(InterruptedException::class)
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>,
        generationId: Long
    ) {
        val columnNames =
            if (includeCdcDeletedAt) FINAL_TABLE_COLUMN_NAMES_CDC else FINAL_TABLE_COLUMN_NAMES
        val cdcDeletedAtDecl = if (includeCdcDeletedAt) ",`_ab_cdc_deleted_at` TIMESTAMP" else ""
        val cdcDeletedAtName = if (includeCdcDeletedAt) ",`_ab_cdc_deleted_at`" else ""
        val recordsText =
            records
                .stream() // For each record, convert it to a string like "(rawId, extractedAt,
                // loadedAt, data)"
                .map { record: JsonNode ->
                    columnNames
                        .stream()
                        .map { fieldName: String? -> record[fieldName] }
                        .map { r: JsonNode? ->
                            if (r == null) {
                                return@map "NULL"
                            }
                            val stringContents =
                                if (r.isTextual) {
                                    r.asText()
                                } else {
                                    r.toString()
                                }
                            '"'.toString() +
                                stringContents // Serialized json might contain backslashes and
                                    // double quotes. Escape them.
                                    .replace("\\", "\\\\")
                                    .replace("\"", "\\\"") +
                                '"'
                        }
                        .collect(Collectors.joining(","))
                }
                .map { row: String -> "($row)" }
                .collect(Collectors.joining(","))

        bq!!.query(
            QueryJobConfiguration.newBuilder(
                    StringSubstitutor(
                            Map.of(
                                "final_table_id",
                                streamId.finalTableId(BigQuerySqlGenerator.QUOTE, suffix!!),
                                "cdc_deleted_at_name",
                                cdcDeletedAtName,
                                "cdc_deleted_at_decl",
                                cdcDeletedAtDecl,
                                "records",
                                recordsText
                            )
                        )
                        .replace( // Similar to insertRawTableRecords, some of these columns are
                            // declared as string and wrapped in
                            // parse_json().
                            // There's also a bunch of casting, because bigquery doesn't coerce
                            // strings to e.g. int
                            """
                insert into ${'$'}{final_table_id} (
                  _airbyte_raw_id,
                  _airbyte_extracted_at,
                  _airbyte_meta,
                  _airbyte_generation_id,
                  `id1`,
                  `id2`,
                  `updated_at`,
                  `struct`,
                  `array`,
                  `string`,
                  `number`,
                  `integer`,
                  `boolean`,
                  `timestamp_with_timezone`,
                  `timestamp_without_timezone`,
                  `time_with_timezone`,
                  `time_without_timezone`,
                  `date`,
                  `unknown`
                  ${'$'}{cdc_deleted_at_name}
                )
                select
                  _airbyte_raw_id,
                  _airbyte_extracted_at,
                  parse_json(_airbyte_meta),
                  _airbyte_generation_id,
                  cast(`id1` as int64),
                  cast(`id2` as int64),
                  `updated_at`,
                  parse_json(`struct`),
                  parse_json(`array`),
                  `string`,
                  cast(`number` as numeric),
                  cast(`integer` as int64),
                  cast(`boolean` as boolean),
                  `timestamp_with_timezone`,
                  `timestamp_without_timezone`,
                  `time_with_timezone`,
                  `time_without_timezone`,
                  `date`,
                  parse_json(`unknown`)
                  ${'$'}{cdc_deleted_at_name}
                from unnest([
                  STRUCT<
                    _airbyte_raw_id STRING,
                    _airbyte_extracted_at TIMESTAMP,
                    _airbyte_meta STRING,
                    _airbyte_generation_id INTEGER,
                    `id1` STRING,
                    `id2` STRING,
                    `updated_at` TIMESTAMP,
                    `struct` STRING,
                    `array` STRING,
                    `string` STRING,
                    `number` STRING,
                    `integer` STRING,
                    `boolean` STRING,
                    `timestamp_with_timezone` TIMESTAMP,
                    `timestamp_without_timezone` DATETIME,
                    `time_with_timezone` STRING,
                    `time_without_timezone` TIME,
                    `date` DATE,
                    `unknown` STRING
                    ${'$'}{cdc_deleted_at_decl}
                  >
                  ${'$'}{records}
                ])
                
                """.trimIndent()
                        )
                )
                .build()
        )
    }

    private fun stringifyRecords(records: List<JsonNode>, columnNames: List<String>): String {
        return records
            .stream() // For each record, convert it to a string like "(rawId, extractedAt,
            // loadedAt, data)"
            .map { record: JsonNode ->
                columnNames
                    .stream()
                    .map { fieldName: String? -> record[fieldName] }
                    .map { r: JsonNode? ->
                        if (r == null) {
                            return@map "NULL"
                        }
                        val stringContents =
                            if (r.isTextual) {
                                r.asText()
                            } else {
                                r.toString()
                            }
                        '"'.toString() +
                            stringContents // Serialized json might contain backslashes and double
                                // quotes. Escape them.
                                .replace("\\", "\\\\")
                                .replace("\"", "\\\"") +
                            '"'
                    }
                    .collect(Collectors.joining(","))
            }
            .map { row: String -> "($row)" }
            .collect(Collectors.joining(","))
    }

    @Throws(InterruptedException::class)
    override fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        val recordsText =
            stringifyRecords(records, JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES_WITH_GENERATION)

        bq!!.query(
            QueryJobConfiguration.newBuilder(
                    StringSubstitutor(
                            Map.of(
                                "raw_table_id",
                                streamId.rawTableId(BigQuerySqlGenerator.QUOTE),
                                "records",
                                recordsText
                            )
                        )
                        .replace( // TODO: Perform a normal insert - edward
                            """
                INSERT INTO ${'$'}{raw_table_id} (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_loaded_at, _airbyte_data, _airbyte_meta, _airbyte_generation_id)
                SELECT _airbyte_raw_id, _airbyte_extracted_at, _airbyte_loaded_at, _airbyte_data, _airbyte_meta, cast(_airbyte_generation_id as int64) FROM UNNEST([
                  STRUCT<`_airbyte_raw_id` STRING, `_airbyte_extracted_at` TIMESTAMP, `_airbyte_loaded_at` TIMESTAMP, _airbyte_data STRING, _airbyte_meta STRING, `_airbyte_generation_id` STRING>
                  ${'$'}{records}
                ])
                
                """.trimIndent()
                        )
                )
                .build()
        )
    }

    @Throws(Exception::class)
    override fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        val recordsText = stringifyRecords(records, JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS)
        bq!!.query(
            QueryJobConfiguration.newBuilder(
                    StringSubstitutor(
                            Map.of(
                                "v1_raw_table_id",
                                streamId.rawTableId(BigQuerySqlGenerator.QUOTE),
                                "records",
                                recordsText
                            )
                        )
                        .replace(
                            """
                        INSERT INTO ${'$'}{v1_raw_table_id} (_airbyte_ab_id, _airbyte_data, _airbyte_emitted_at)
                        SELECT _airbyte_ab_id, _airbyte_data, _airbyte_emitted_at FROM UNNEST([
                          STRUCT<`_airbyte_ab_id` STRING, _airbyte_data STRING, `_airbyte_emitted_at` TIMESTAMP>
                          ${'$'}{records}
                        ])
                        
                        """.trimIndent()
                        )
                )
                .build()
        )
    }

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamId: StreamId): List<JsonNode> {
        val result =
            bq!!.query(
                QueryJobConfiguration.of(
                    "SELECT * FROM " + streamId.rawTableId(BigQuerySqlGenerator.QUOTE)
                )
            )
        return toJsonRecords(result)
    }

    @Throws(Exception::class)
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun dumpFinalTableRecords(streamId: StreamId, suffix: String?): List<JsonNode> {
        val result =
            bq!!.query(
                QueryJobConfiguration.of(
                    "SELECT * FROM " + streamId.finalTableId(BigQuerySqlGenerator.QUOTE, suffix!!)
                )
            )
        return toJsonRecords(result)
    }

    override fun teardownNamespace(namespace: String) {
        bq!!.delete(namespace, BigQuery.DatasetDeleteOption.deleteContents())
    }

    override val supportsSafeCast: Boolean
        get() = true

    @Test
    @Throws(Exception::class)
    override fun testCreateTableIncremental() {
        destinationHandler.execute(generator.createTable(incrementalDedupStream, "", false))

        val table = bq!!.getTable(namespace, "users_final")
        // The table should exist
        Assertions.assertNotNull(table)
        val schema = table.getDefinition<TableDefinition>().schema
        // And we should know exactly what columns it contains
        Assertions
            .assertEquals( // Would be nice to assert directly against StandardSQLTypeName, but
                // bigquery returns schemas of
                // LegacySQLTypeName. So we have to translate.
                Schema.of(
                    Field.newBuilder(
                            "_airbyte_raw_id",
                            LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.STRING)
                        )
                        .setMode(Field.Mode.REQUIRED)
                        .build(),
                    Field.newBuilder(
                            "_airbyte_extracted_at",
                            LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)
                        )
                        .setMode(Field.Mode.REQUIRED)
                        .build(),
                    Field.newBuilder(
                            "_airbyte_meta",
                            LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.JSON)
                        )
                        .setMode(Field.Mode.REQUIRED)
                        .build(),
                    Field.newBuilder(
                            "_airbyte_generation_id",
                            LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.INT64)
                        )
                        .build(),
                    Field.of("id1", LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.INT64)),
                    Field.of("id2", LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.INT64)),
                    Field.of(
                        "updated_at",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)
                    ),
                    Field.of(
                        "struct",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.JSON)
                    ),
                    Field.of(
                        "array",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.JSON)
                    ),
                    Field.of(
                        "string",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.STRING)
                    ),
                    Field.of(
                        "number",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.NUMERIC)
                    ),
                    Field.of(
                        "integer",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.INT64)
                    ),
                    Field.of(
                        "boolean",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.BOOL)
                    ),
                    Field.of(
                        "timestamp_with_timezone",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)
                    ),
                    Field.of(
                        "timestamp_without_timezone",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.DATETIME)
                    ),
                    Field.of(
                        "time_with_timezone",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.STRING)
                    ),
                    Field.of(
                        "time_without_timezone",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.TIME)
                    ),
                    Field.of("date", LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.DATE)),
                    Field.of(
                        "unknown",
                        LegacySQLTypeName.legacySQLTypeName(StandardSQLTypeName.JSON)
                    )
                ),
                schema
            )
        // TODO this should assert partitioning/clustering configs
    }

    @Test
    @Throws(InterruptedException::class)
    fun testCreateTableInOtherRegion() {
        val destinationHandler = BigQueryDestinationHandler(bq!!, "asia-east1")
        // We're creating the dataset in the wrong location in the @BeforeEach block. Explicitly
        // delete it.
        bq!!.getDataset(namespace).delete()
        val sqlGenerator = BigQuerySqlGenerator(projectId, "asia-east1")
        destinationHandler.execute(sqlGenerator.createSchema(namespace))
        destinationHandler.execute(sqlGenerator.createTable(incrementalDedupStream, "", false))

        // Empirically, it sometimes takes Bigquery nearly 30 seconds to propagate the dataset's
        // existence.
        // Give ourselves 2 minutes just in case.
        for (i in 0..119) {
            val dataset = bq!!.getDataset(DatasetId.of(bq!!.options.projectId, namespace))
            if (dataset == null) {
                LOGGER.info("Sleeping and trying again... ({})", i)
                Thread.sleep(1000)
            } else {
                Assertions.assertEquals("asia-east1", dataset.location)
                return
            }
        }
        Assertions.fail<Any>("Dataset does not exist")
    }

    /**
     * Bigquery column names aren't allowed to start with certain prefixes. Verify that we throw an
     * error in these cases.
     */
    @ParameterizedTest
    @ValueSource(
        strings =
            ["_table_", "_file_", "_partition_", "_row_timestamp_", "__root__", "_colidentifier_"]
    )
    fun testFailureOnReservedColumnNamePrefix(prefix: String) {
        val columns = java.util.LinkedHashMap<ColumnId, AirbyteType>()
        columns[generator.buildColumnId(prefix + "the_column_name")] = AirbyteProtocolType.STRING
        val stream =
            StreamConfig(
                streamId,
                ImportType.APPEND,
                emptyList(),
                Optional.empty(),
                columns,
                0,
                0,
                0
            )

        val createTable = generator.createTable(stream, "", false)
        Assertions.assertThrows(BigQueryException::class.java) {
            destinationHandler.execute(createTable)
        }
    }

    /**
     * Something about this test is borked on bigquery. It fails because the raw table doesn't
     * exist, but you can go into the UI and see that it does exist.
     */
    @Disabled
    @Throws(Exception::class)
    override fun noCrashOnSpecialCharacters(specialChars: String) {
        super.noCrashOnSpecialCharacters(specialChars)
    }

    /**
     * Bigquery doesn't handle frequent INSERT/DELETE statements on a single table very well. So we
     * don't have real state handling. Disable this test.
     */
    @Disabled
    @Test
    @Throws(Exception::class)
    override fun testStateHandling() {
        super.testStateHandling()
    }

    @Disabled
    override fun testLongIdentifierHandling() {
        super.testLongIdentifierHandling()
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(BigQuerySqlGeneratorIntegrationTest::class.java)

        private var bq: BigQuery? = null
        private var projectId: String? = null
        private var datasetLocation: String? = null

        @BeforeAll
        @Throws(Exception::class)
        @JvmStatic
        fun setupBigquery() {
            val rawConfig = Files.readString(Path.of("secrets/credentials-gcs-staging.json"))
            val config = deserialize(rawConfig)
            bq = getBigQuery(config)

            projectId = config[BigQueryConsts.CONFIG_PROJECT_ID].asText()
            datasetLocation = config[BigQueryConsts.CONFIG_DATASET_LOCATION].asText()
        }

        /**
         * TableResult contains records in a somewhat nonintuitive format (and it avoids loading
         * them all into memory). That's annoying for us since we're working with small test data,
         * so just pull everything into a list.
         */
        fun toJsonRecords(result: TableResult): List<JsonNode> {
            return result
                .streamAll()
                .map { row: FieldValueList -> toJson(result.schema!!, row) }
                .toList()
        }

        /**
         * FieldValueList stores everything internally as string (I think?) but provides conversions
         * to more useful types. This method does that conversion, using the schema to determine
         * which type is most appropriate. Then we just dump everything into a jsonnode for interop
         * with RecordDiffer.
         */
        private fun toJson(schema: Schema, row: FieldValueList): JsonNode {
            val json = emptyObject() as ObjectNode
            for (i in schema.fields.indices) {
                val field = schema.fields[i]
                val value = row[i]
                val typedValue: JsonNode
                if (!value.isNull) {
                    typedValue =
                        when (field.type.standardType) {
                            StandardSQLTypeName.BOOL -> jsonNode(value.booleanValue)
                            StandardSQLTypeName.INT64 -> jsonNode(value.longValue)
                            StandardSQLTypeName.FLOAT64 -> jsonNode(value.doubleValue)
                            StandardSQLTypeName.NUMERIC,
                            StandardSQLTypeName.BIGNUMERIC -> jsonNode(value.numericValue)
                            StandardSQLTypeName.STRING -> jsonNode(value.stringValue)
                            StandardSQLTypeName.TIMESTAMP ->
                                jsonNode(value.timestampInstant.toString())
                            StandardSQLTypeName.DATE,
                            StandardSQLTypeName.DATETIME,
                            StandardSQLTypeName.TIME -> jsonNode(value.stringValue)
                            StandardSQLTypeName.JSON ->
                                jsonNode(deserializeExact(value.stringValue))
                            else -> jsonNode(value.stringValue)
                        }
                    json.set<JsonNode>(field.name, typedValue)
                }
            }
            return json
        }
    }
}
