/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.Database
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.Companion.`in`
import org.jooq.DSLContext
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import java.util.*
import java.util.concurrent.Callable
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.function.Consumer

@TestInstance(TestInstance.Lifecycle.PER_METHOD)
@Execution(ExecutionMode.CONCURRENT)
class CdcMssqlSourceDatatypeTest : AbstractMssqlSourceDatatypeTest() {
    private val executor: ExecutorService = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors())
    override val isCdcTest = false

    override val config: JsonNode
        get() = testdb!!.integrationTestConfigBuilder()
            .withCdcReplication()
            .withoutSsl()
            .build()

    override fun setupDatabase(): Database? {
        testdb = `in`(MsSQLTestDatabase.BaseImage.MSSQL_2022, MsSQLTestDatabase.ContainerModifier.AGENT)
            .withCdc()
        return testdb!!.database
    }

    @Throws(Exception::class)
    override fun createTables() {
        val createTableTasks: MutableList<Callable<MsSQLTestDatabase>> = ArrayList()
        val enableCdcForTableTasks: MutableList<Callable<MsSQLTestDatabase>> = ArrayList()
        for (test in testDataHolders) {
            createTableTasks.add(Callable { testdb!!.with(test.createSqlQuery) })
            enableCdcForTableTasks.add(Callable { testdb!!.withCdcForTable(test.nameSpace, test.nameWithTestPrefix, null) })
        }
        executor.invokeAll(createTableTasks)
        executor.invokeAll(enableCdcForTableTasks)
    }

    @Throws(Exception::class)
    override fun populateTables() {
        val insertTasks: MutableList<Callable<MsSQLTestDatabase?>> = ArrayList()
        val waitForCdcRecordsTasks: MutableList<Callable<MsSQLTestDatabase?>> = ArrayList()
        for (test in testDataHolders) {
            insertTasks.add(Callable {
                database!!.query<Any?> { ctx: DSLContext ->
                    val sql = test.insertSqlQueries
                    Objects.requireNonNull(ctx)
                    sql.forEach(Consumer { sql: String? -> ctx.fetch(sql) })
                    null
                }
                null
            })
            waitForCdcRecordsTasks.add(Callable { testdb!!.waitForCdcRecords(test.nameSpace, test.nameWithTestPrefix, test.expectedValues.size) })
        }
        // executor.invokeAll(insertTasks);
        executor.invokeAll(insertTasks)
        executor.invokeAll(waitForCdcRecordsTasks)
    }

    public override fun testCatalog(): Boolean {
        return true
    }
}
