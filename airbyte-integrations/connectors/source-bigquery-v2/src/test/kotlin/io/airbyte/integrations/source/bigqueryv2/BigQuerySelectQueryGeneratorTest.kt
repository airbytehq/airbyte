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
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigQuerySelectQueryGeneratorTest {

    private val generator = BigQuerySourceOperations()
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
                "CAST(`tod` AS STRING) AS `tod`, `updated_at` FROM `sales`.`orders` " +
                "WHERE `day` > ? ORDER BY `day`",
            query.sql,
        )
        val max: SelectQuery =
            generator.generate(
                SelectQuerySpec(SelectColumnMaxValue(tod), From("orders", "sales")).optimize()
            )
        Assertions.assertEquals("SELECT CAST(MAX(`tod`) AS STRING) FROM `sales`.`orders`", max.sql)
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
            "SELECT `id`, TO_JSON_STRING(`address`) AS `address`, TO_JSON_STRING(`tags`) AS `tags` FROM `sales`.`orders`",
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
        Assertions.assertEquals("SELECT `id`, `name` FROM `sales`.`orders` LIMIT 0", query.sql)
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
            "SELECT `id` FROM `sales`.`orders` ORDER BY `id` LIMIT 1000",
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
            "SELECT `id`, `updated_at` FROM `sales`.`orders` WHERE (`id` > ?) AND (`updated_at` <= ?) ORDER BY `id` LIMIT 10",
            query.sql,
        )
        Assertions.assertEquals(
            listOf(
                SelectQuery.Binding(Jsons.numberNode(10), LongFieldType),
                SelectQuery.Binding(
                    Jsons.textNode("2026-01-01T00:00:00Z"),
                    OffsetDateTimeFieldType
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
        Assertions.assertEquals("SELECT MAX(`updated_at`) FROM `sales`.`orders`", query.sql)
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
            "SELECT `id`, `name` FROM (SELECT * FROM `sales`.`orders` TABLESAMPLE SYSTEM (0.39062500 PERCENT) LIMIT 1024)",
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
            "SELECT `id` FROM (SELECT * FROM `sales`.`orders` WHERE `id` > ? LIMIT 1024)",
            unsampled.sql,
        )
        Assertions.assertEquals(1, unsampled.bindings.size)
    }

    @Test
    fun testIdentifierQuoting() {
        val weird = EmittedField("we`ird", StringFieldType)
        val query: SelectQuery =
            generator.generate(SelectQuerySpec(SelectColumns(weird), From("t-1", "my dataset")))
        Assertions.assertEquals("SELECT `we\\`ird` FROM `my dataset`.`t-1`", query.sql)
    }
}
