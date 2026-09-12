/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.google.cloud.NoCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryOptions
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
import com.google.cloud.bigquery.ViewDefinition
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.BigQueryEmulatorContainer
import org.testcontainers.utility.DockerImageName

private val log = KotlinLogging.logger {}

/**
 * Shared `ghcr.io/goccy/bigquery-emulator` container for the tests, seeded with the parity dataset.
 *
 * The emulator does not authenticate requests; the connector is pointed at it through the
 * [BigQueryEmulator.SYSTEM_PROPERTY] system property, which the in-process CLI runner picks up.
 * Emulator deviations from BigQuery worth knowing when reading the fixtures:
 * - `tableConstraints` passed to `tables.insert` are echoed back by `tables.get`, but a DDL
 * `PRIMARY KEY ... NOT ENFORCED` clause is dropped;
 * - `NOT NULL` columns of DDL-created tables come back as `NULLABLE` (`tables.insert` keeps `REQUIRED`);
 * - `INFORMATION_SCHEMA` only has `SCHEMATA`, `TABLES`, `TABLE_OPTIONS` and `COLUMNS`;
 * - a `FLOAT64` nested in an `ARRAY<STRUCT<...>>` cannot be inserted into (type mismatch FLOAT vs
 * DOUBLE).
 */
object BigQueryEmulatorTestFixture {
    val IMAGE: DockerImageName =
        DockerImageName.parse("ghcr.io/goccy/bigquery-emulator:0.8.1")
            .asCompatibleSubstituteFor("ghcr.io/goccy/bigquery-emulator")

    const val PROJECT_ID = "test-project"
    const val DATASET = "airbyte_test"
    const val OTHER_DATASET = "other_dataset"
    const val EMPTY_DATASET = "empty_dataset"

    /** A service account key the emulator never validates. */
    const val DUMMY_CREDENTIALS_JSON =
        """{"type":"service_account","client_email":"airbyte@test-project.iam.gserviceaccount.com","private_key":"unused"}"""

    private val container: BigQueryEmulatorContainer by lazy {
        BigQueryEmulatorContainer(IMAGE).also {
            it.start()
            seed(client(it.emulatorHttpEndpoint))
        }
    }

    /** Starts (once) and points the connector at the emulator. */
    fun start(): BigQueryEmulatorContainer {
        val started: BigQueryEmulatorContainer = container
        System.setProperty(BigQueryEmulator.SYSTEM_PROPERTY, started.emulatorHttpEndpoint)
        return started
    }

    fun client(endpoint: String): BigQuery =
        BigQueryOptions.newBuilder()
            .setHost(endpoint)
            .setProjectId(PROJECT_ID)
            .setCredentials(NoCredentials.getInstance())
            .build()
            .service

    fun config(
        projectId: String = PROJECT_ID,
        datasetId: String? = null,
        credentialsJson: String? = DUMMY_CREDENTIALS_JSON,
    ): BigQuerySourceConfigurationSpecification {
        val node = Jsons.objectNode().put("project_id", projectId)
        datasetId?.let { node.put("dataset_id", it) }
        credentialsJson?.let { node.put("credentials_json", it) }
        return Jsons.readValue(
            Jsons.writeValueAsString(node),
            BigQuerySourceConfigurationSpecification::class.java,
        )
    }

    private fun nullable(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
        Field.newBuilder(name, type, *sub).setMode(Field.Mode.NULLABLE).build()

    private fun required(name: String, type: StandardSQLTypeName): Field =
        Field.newBuilder(name, type).setMode(Field.Mode.REQUIRED).build()

    private fun repeated(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
        Field.newBuilder(name, type, *sub).setMode(Field.Mode.REPEATED).build()

    /**
     * Seeds the datasets used by the check and discover tests: every BigQuery type, nested
     * `STRUCT`/`ARRAY` columns, a table with a `PRIMARY KEY`, a view, a table without rows, a
     * second dataset and a dataset without tables. The default `--project` dataset of the container
     * image (if any) is left alone.
     */
    fun seed(bigquery: BigQuery) {
        log.info { "Seeding the BigQuery emulator." }
        for (dataset in listOf(DATASET, OTHER_DATASET, EMPTY_DATASET)) {
            bigquery.create(DatasetInfo.newBuilder(DatasetId.of(PROJECT_ID, dataset)).build())
        }
        val allTypes: Schema =
            Schema.of(
                required("id", StandardSQLTypeName.INT64),
                nullable("name", StandardSQLTypeName.STRING),
                nullable("price", StandardSQLTypeName.NUMERIC),
                nullable("big", StandardSQLTypeName.BIGNUMERIC),
                nullable("ratio", StandardSQLTypeName.FLOAT64),
                nullable("active", StandardSQLTypeName.BOOL),
                nullable("blob", StandardSQLTypeName.BYTES),
                nullable("day", StandardSQLTypeName.DATE),
                nullable("local_ts", StandardSQLTypeName.DATETIME),
                nullable("ts", StandardSQLTypeName.TIMESTAMP),
                nullable("tod", StandardSQLTypeName.TIME),
                nullable("geo", StandardSQLTypeName.GEOGRAPHY),
                nullable("doc", StandardSQLTypeName.JSON),
                nullable("span", StandardSQLTypeName.INTERVAL),
                nullable(
                    "address",
                    StandardSQLTypeName.STRUCT,
                    nullable("city", StandardSQLTypeName.STRING),
                    nullable("zip", StandardSQLTypeName.INT64),
                    nullable(
                        "geo",
                        StandardSQLTypeName.STRUCT,
                        nullable("observed_at", StandardSQLTypeName.TIME)
                    ),
                ),
                repeated("tags", StandardSQLTypeName.STRING),
                repeated(
                    "line_items",
                    StandardSQLTypeName.STRUCT,
                    nullable("sku", StandardSQLTypeName.STRING),
                    nullable("qty", StandardSQLTypeName.INT64),
                    repeated(
                        "discounts",
                        StandardSQLTypeName.STRUCT,
                        nullable("code", StandardSQLTypeName.STRING),
                        nullable("pct", StandardSQLTypeName.INT64),
                    ),
                ),
            )
        bigquery.create(
            TableInfo.of(
                TableId.of(PROJECT_ID, DATASET, "all_types"),
                StandardTableDefinition.of(allTypes)
            )
        )
        bigquery.query(
            QueryJobConfiguration.of(
                """
INSERT INTO `$DATASET`.`all_types` VALUES (
  1, 'alice', NUMERIC '1.5', BIGNUMERIC '2.5', 0.25, TRUE, b'abc', DATE '2021-10-20',
  DATETIME '2021-10-20 11:22:33', TIMESTAMP '2021-10-20 11:22:33', TIME '15:30:00',
  ST_GEOGFROMTEXT('POINT(1 2)'), JSON '{"a":1}', MAKE_INTERVAL(2021, 10, 10, 10, 10, 10),
  STRUCT('Paris' AS city, 75001 AS zip, STRUCT(TIME '08:00:00' AS observed_at) AS geo), ['a', 'b'],
  [STRUCT('sku-1' AS sku, 2 AS qty, [STRUCT('SUMMER' AS code, 10 AS pct)] AS discounts)]
)
"""
            )
        )
        // Unenforced primary key, persisted by the emulator when set through tables.insert.
        bigquery.create(
            TableInfo.newBuilder(
                    TableId.of(PROJECT_ID, DATASET, "with_pk"),
                    StandardTableDefinition.of(
                        Schema.of(
                            required("order_id", StandardSQLTypeName.INT64),
                            required("line", StandardSQLTypeName.INT64),
                            nullable("updated_at", StandardSQLTypeName.TIMESTAMP),
                        )
                    ),
                )
                .setTableConstraints(
                    TableConstraints.newBuilder()
                        .setPrimaryKey(
                            PrimaryKey.newBuilder().setColumns(listOf("order_id", "line")).build()
                        )
                        .build()
                )
                .build()
        )
        bigquery.create(
            TableInfo.of(
                TableId.of(PROJECT_ID, DATASET, "no_rows"),
                StandardTableDefinition.of(
                    Schema.of(
                        nullable("k", StandardSQLTypeName.STRING),
                        nullable("v", StandardSQLTypeName.FLOAT64)
                    )
                ),
            )
        )
        bigquery.create(
            TableInfo.of(
                TableId.of(PROJECT_ID, DATASET, "all_types_view"),
                ViewDefinition.of("SELECT id, name, address FROM `$DATASET`.`all_types`"),
            )
        )
        bigquery.create(
            TableInfo.of(
                TableId.of(PROJECT_ID, OTHER_DATASET, "events"),
                StandardTableDefinition.of(
                    Schema.of(
                        nullable("event_id", StandardSQLTypeName.STRING),
                        nullable("occurred_at", StandardSQLTypeName.TIMESTAMP),
                        nullable("payload", StandardSQLTypeName.JSON),
                    )
                ),
            )
        )
    }
}
