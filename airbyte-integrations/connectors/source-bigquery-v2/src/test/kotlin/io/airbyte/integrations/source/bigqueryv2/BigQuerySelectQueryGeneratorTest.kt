/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.FromSample
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.GreaterOrEqual
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.OrderBy
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigQuerySelectQueryGeneratorTest {

    private val generator = BigQuerySourceOperations(dataProjectId = "my-project")
    private val id = EmittedField("id", LongFieldType)
    private val name = EmittedField("name", StringFieldType)
    private val updatedAt = EmittedField("updated_at", OffsetDateTimeFieldType)

    @Test
    fun testTemporalColumnsAreReadAsText() {
        val day = EmittedField("day", BigQueryDateFieldType)
        val localTs = EmittedField("local_ts", BigQueryDateTimeFieldType)
        val tod = EmittedField("tod", BigQueryTimeFieldType)
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(
                        SelectColumns(id, day, localTs, tod, updatedAt),
                        From("orders", "sales"),
                        Where(Greater(day, Jsons.textNode("2021-10-20"))),
                        OrderBy(day),
                    )
                    .optimize()
            )
        Assertions.assertEquals(
            "SELECT `id`, CAST(`day` AS STRING) AS `day`, CAST(`local_ts` AS STRING) AS `local_ts`, " +
                "CAST(`tod` AS STRING) AS `tod`, `updated_at` FROM `my-project`.`sales`.`orders` " +
                "WHERE `day` > CAST(? AS DATE) ORDER BY `day`",
            query.sql,
        )
        val max: SelectQuery =
            generator.generate(
                SelectQuerySpec(SelectColumnMaxValue(tod), From("orders", "sales")).optimize()
            )
        Assertions.assertEquals(
            "SELECT CAST(MAX(`tod`) AS STRING) FROM `my-project`.`sales`.`orders`",
            max.sql
        )
    }

    @Test
    fun testNestedColumnsAreReadAsJsonText() {
        val address =
            EmittedField(
                "address",
                BigQueryStructFieldType(listOf(EmittedField("city", StringFieldType)))
            )
        val tags = EmittedField("tags", BigQueryArrayFieldType(StringFieldType))
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(SelectColumns(id, address, tags), From("orders", "sales"))
                    .optimize()
            )
        Assertions.assertEquals(
            "SELECT `id`, TO_JSON_STRING(`address`) AS `address`, TO_JSON_STRING(`tags`) AS `tags` FROM `my-project`.`sales`.`orders`",
            query.sql,
        )
    }

    @Test
    fun testSelectLimitZero() {
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(SelectColumns(id, name), From("orders", "sales"), limit = Limit(0))
                    .optimize()
            )
        Assertions.assertEquals(
            "SELECT `id`, `name` FROM `my-project`.`sales`.`orders` LIMIT 0",
            query.sql
        )
        Assertions.assertEquals(emptyList<SelectQuery.Binding>(), query.bindings)
        Assertions.assertEquals(listOf(id, name), query.columns)
    }

    @Test
    fun testLimitIsALiteral() {
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(
                    SelectColumns(id),
                    From("orders", "sales"),
                    orderBy = OrderBy(id),
                    limit = Limit(1000),
                )
            )
        Assertions.assertEquals(
            "SELECT `id` FROM `my-project`.`sales`.`orders` ORDER BY `id` LIMIT 1000",
            query.sql,
        )
        Assertions.assertEquals(emptyList<SelectQuery.Binding>(), query.bindings)
    }

    @Test
    fun testWhereBindings() {
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(
                    SelectColumns(id, updatedAt),
                    From("orders", "sales"),
                    Where(
                        And(
                            Greater(id, Jsons.numberNode(10)),
                            LesserOrEqual(updatedAt, Jsons.textNode("2026-01-01T00:00:00Z")),
                        )
                    ),
                    OrderBy(id),
                    Limit(10),
                )
            )
        Assertions.assertEquals(
            "SELECT `id`, `updated_at` FROM `my-project`.`sales`.`orders` WHERE (`id` > ?) AND (`updated_at` <= CAST(? AS TIMESTAMP)) ORDER BY `id` LIMIT 10",
            query.sql,
        )
        Assertions.assertEquals(
            listOf(
                SelectQuery.Binding(Jsons.numberNode(10), LongFieldType),
                // TIMESTAMP is bound as text + CAST so microseconds survive (setTimestamp truncates
                // to milliseconds).
                SelectQuery.Binding(Jsons.textNode("2026-01-01T00:00:00Z"), StringFieldType),
            ),
            query.bindings,
        )
    }

    @Test
    fun testCursorBoundsThatNeedACastAreBoundAsString() {
        // Regression: DATE/DATETIME/TIME, TIMESTAMP and BIGNUMERIC columns are compared natively,
        // but
        // no JDBC setter produces a matching, full-precision parameter (setTimestamp binds a
        // millisecond TIMESTAMP even for DATETIME, setBigDecimal binds a NUMERIC even for
        // BIGNUMERIC),
        // so BigQuery rejected the comparison or lost microseconds. Each bound is bound as a STRING
        // and
        // cast back to the column's BigQuery type; the decimal bound is a plain number (never
        // scientific).
        val dt = EmittedField("dt", BigQueryDateTimeFieldType)
        val day = EmittedField("day", BigQueryDateFieldType)
        val tod = EmittedField("tod", BigQueryTimeFieldType)
        val ts = EmittedField("ts", OffsetDateTimeFieldType)
        val big = EmittedField("big", BigQueryBigNumericFieldType)
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(
                    SelectColumns(id),
                    From("users", "ds"),
                    Where(
                        And(
                            GreaterOrEqual(dt, Jsons.textNode("2024-01-10T20:53:31.000000")),
                            LesserOrEqual(day, Jsons.textNode("2024-06-01")),
                            LesserOrEqual(tod, Jsons.textNode("15:30:00.000001")),
                            GreaterOrEqual(ts, Jsons.textNode("2024-12-31T17:18:19.000005Z")),
                            LesserOrEqual(
                                big,
                                Jsons.numberNode(BigDecimal("3300000000000000000000000000000"))
                            ),
                        )
                    ),
                )
            )
        Assertions.assertEquals(
            "SELECT `id` FROM `my-project`.`ds`.`users` WHERE " +
                "(`dt` >= CAST(? AS DATETIME)) AND (`day` <= CAST(? AS DATE)) AND " +
                "(`tod` <= CAST(? AS TIME)) AND (`ts` >= CAST(? AS TIMESTAMP)) AND " +
                "(`big` <= CAST(? AS BIGNUMERIC))",
            query.sql,
        )
        Assertions.assertEquals(
            listOf(
                SelectQuery.Binding(Jsons.textNode("2024-01-10T20:53:31.000000"), StringFieldType),
                SelectQuery.Binding(Jsons.textNode("2024-06-01"), StringFieldType),
                SelectQuery.Binding(Jsons.textNode("15:30:00.000001"), StringFieldType),
                SelectQuery.Binding(Jsons.textNode("2024-12-31T17:18:19.000005Z"), StringFieldType),
                SelectQuery.Binding(
                    Jsons.textNode("3300000000000000000000000000000"),
                    StringFieldType
                ),
            ),
            query.bindings,
        )
    }

    @Test
    fun testMaxCursorValue() {
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(SelectColumnMaxValue(updatedAt), From("orders", "sales"))
            )
        Assertions.assertEquals(
            "SELECT MAX(`updated_at`) FROM `my-project`.`sales`.`orders`",
            query.sql
        )
    }

    @Test
    fun testSamplingQuery() {
        val query: SelectQuery =
            generator.generate(
                SelectQuerySpec(
                    SelectColumns(id, name),
                    FromSample("orders", "sales", sampleRateInvPow2 = 8, sampleSize = 1024),
                )
            )
        Assertions.assertEquals(
            "SELECT `id`, `name` FROM (SELECT * FROM `my-project`.`sales`.`orders` TABLESAMPLE SYSTEM (0.39062500 PERCENT) LIMIT 1024)",
            query.sql,
        )
        val unsampled: SelectQuery =
            generator.generate(
                SelectQuerySpec(
                    SelectColumns(id),
                    FromSample(
                        "orders",
                        "sales",
                        sampleRateInvPow2 = 0,
                        sampleSize = 1024,
                        where = Where(Greater(id, Jsons.numberNode(5))),
                    ),
                )
            )
        Assertions.assertEquals(
            "SELECT `id` FROM (SELECT * FROM `my-project`.`sales`.`orders` WHERE `id` > ? LIMIT 1024)",
            unsampled.sql,
        )
        Assertions.assertEquals(1, unsampled.bindings.size)
    }

    @Test
    fun testIdentifierQuoting() {
        val weird = EmittedField("we`ird", StringFieldType)
        val query: SelectQuery =
            generator.generate(SelectQuerySpec(SelectColumns(weird), From("t-1", "my dataset")))
        Assertions.assertEquals("SELECT `we\\`ird` FROM `my-project`.`my dataset`.`t-1`", query.sql)
        val otherProject = BigQuerySourceOperations(dataProjectId = "data`project")
        Assertions.assertEquals(
            "SELECT `id` FROM `data\\`project`.`sales`.`orders`",
            otherProject.generate(SelectQuerySpec(SelectColumns(id), From("orders", "sales"))).sql,
        )
    }
}
