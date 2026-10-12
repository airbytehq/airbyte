/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.DatasetId
import com.google.cloud.bigquery.DatasetInfo
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.PrimaryKey
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableConstraints
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableInfo
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * READ through the JDBC fallback path (the emulator declines the Storage Read API), exercising
 * [BigQueryConcurrentPartitionsCreator]: a table with a single integer primary key is split into
 * key ranges from `APPROX_QUANTILES`, while a table with no key is read by one query. The forced
 * split (one row per partition, via [BigQueryReadApiConstants.fallbackPartitionTargetRows]) proves
 * the ranges tile the key space with neither gaps nor overlaps end to end.
 */
class BigQueryConcurrentReadTest {

    private val config = BigQueryEmulatorTestFixture.config(datasetId = DATASET)

    @Test
    fun testKeyedTableIsSplitOnQuantilesAndTilesTheKeySpace() {
        // fallback-partition-target-rows=1 makes the 6-row table split into as many ranges as
        // APPROX_QUANTILES yields distinct interior boundaries.
        val output: BufferingOutputConsumer =
            withTargetRows(1) {
                read(configured(discover().stream("keyed"), SyncMode.FULL_REFRESH))
            }
        Assertions.assertEquals(
            (1L..6L).toList(),
            output.records().map { it.data["id"].asLong() }.sorted(),
            output.dump(),
        )
        Assertions.assertEquals(
            listOf(
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
            ),
            output.statuses("keyed"),
            output.dump(),
        )
    }

    @Test
    fun testKeylessTableIsReadByASingleQuery() {
        val output: BufferingOutputConsumer =
            withTargetRows(1) {
                read(configured(discover().stream("no_key"), SyncMode.FULL_REFRESH))
            }
        Assertions.assertEquals(
            listOf("a", "b"),
            output.records().map { it.data["v"].asText() }.sorted(),
            output.dump(),
        )
    }

    private fun discover(): AirbyteCatalog =
        CliRunner.source("discover", config).run().catalogs().single()

    private fun read(vararg streams: ConfiguredAirbyteStream): BufferingOutputConsumer =
        CliRunner.source("read", config, ConfiguredAirbyteCatalog().withStreams(streams.toList()))
            .run()

    private fun configured(stream: AirbyteStream, syncMode: SyncMode): ConfiguredAirbyteStream =
        ConfiguredAirbyteStream()
            .withStream(stream)
            .withSyncMode(syncMode)
            .withCursorField(emptyList())
            .withPrimaryKey(stream.sourceDefinedPrimaryKey)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)

    private fun AirbyteCatalog.stream(name: String): AirbyteStream =
        streams.first { it.name == name }

    private fun BufferingOutputConsumer.statuses(
        stream: String
    ): List<AirbyteStreamStatusTraceMessage.AirbyteStreamStatus> =
        traces()
            .filter { it.type == AirbyteTraceMessage.Type.STREAM_STATUS }
            .map { it.streamStatus }
            .filter { it.streamDescriptor.name == stream }
            .map { it.status }

    private fun BufferingOutputConsumer.dump(): String =
        messages()
            .filter { it.type != io.airbyte.protocol.models.v0.AirbyteMessage.Type.LOG }
            .joinToString("\n") { io.airbyte.cdk.util.Jsons.writeValueAsString(it) }

    private fun <T> withTargetRows(rows: Long, block: () -> T): T {
        val key = "airbyte.connector.extract.bigquery.fallback-partition-target-rows"
        val previous: String? = System.getProperty(key)
        System.setProperty(key, rows.toString())
        try {
            return block()
        } finally {
            if (previous == null) System.clearProperty(key) else System.setProperty(key, previous)
        }
    }

    companion object {
        private const val DATASET = "quantile_ds"

        @JvmStatic
        @BeforeAll
        fun seed() {
            val endpoint: String = BigQueryEmulatorTestFixture.start().emulatorHttpEndpoint
            val bigquery: BigQuery = BigQueryEmulatorTestFixture.client(endpoint)
            val projectId = BigQueryEmulatorTestFixture.PROJECT_ID
            runCatching {
                bigquery.create(DatasetInfo.newBuilder(DatasetId.of(projectId, DATASET)).build())
            }
            bigquery.create(
                TableInfo.newBuilder(
                        TableId.of(projectId, DATASET, "keyed"),
                        StandardTableDefinition.of(
                            Schema.of(
                                Field.newBuilder("id", StandardSQLTypeName.INT64)
                                    .setMode(Field.Mode.REQUIRED)
                                    .build(),
                                Field.of("v", StandardSQLTypeName.STRING),
                            )
                        ),
                    )
                    .setTableConstraints(
                        TableConstraints.newBuilder()
                            .setPrimaryKey(PrimaryKey.newBuilder().setColumns(listOf("id")).build())
                            .build()
                    )
                    .build()
            )
            bigquery.query(
                QueryJobConfiguration.of(
                    "INSERT INTO `$DATASET`.`keyed` VALUES " +
                        "(1,'a'),(2,'b'),(3,'c'),(4,'d'),(5,'e'),(6,'f')"
                )
            )
            bigquery.create(
                TableInfo.of(
                    TableId.of(projectId, DATASET, "no_key"),
                    StandardTableDefinition.of(
                        Schema.of(
                            Field.of("k", StandardSQLTypeName.INT64),
                            Field.of("v", StandardSQLTypeName.STRING),
                        )
                    ),
                )
            )
            bigquery.query(
                QueryJobConfiguration.of("INSERT INTO `$DATASET`.`no_key` VALUES (1,'a'),(2,'b')")
            )
        }
    }
}
