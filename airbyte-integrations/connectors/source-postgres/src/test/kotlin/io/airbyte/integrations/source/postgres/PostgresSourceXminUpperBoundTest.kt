/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase.BaseImage
import java.sql.Connection
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class PostgresSourceXminUpperBoundTest {

    @Test
    @Timeout(value = 300)
    fun `upper bound does not pass the xmin of a row committed after it was taken`() {
        val testdb = PostgresTestDatabase.`in`(BaseImage.POSTGRES_17)
        testdb.with("CREATE TABLE public.xmin_upper_bound(id int)")
        val dataSource = testdb.getDataSource()!!

        dataSource.connection.use { writer ->
            writer.autoCommit = false
            writer.createStatement().use {
                it.execute("INSERT INTO public.xmin_upper_bound VALUES (1)")
            }

            val upperBound =
                dataSource.connection.use { it.queryLong(xminCursorUpperBoundQuery.sql) }
            writer.commit()

            val rowXmin =
                dataSource.connection.use {
                    it.queryLong("SELECT xmin::text::bigint FROM public.xmin_upper_bound")
                }
            assertTrue(
                rowXmin >= upperBound,
                "row committed after the bound has xmin $rowXmin below the bound $upperBound",
            )
        }
    }

    private fun Connection.queryLong(sql: String): Long =
        createStatement().use { stmt ->
            stmt.executeQuery(sql).use { rs ->
                rs.next()
                rs.getLong(1)
            }
        }
}
