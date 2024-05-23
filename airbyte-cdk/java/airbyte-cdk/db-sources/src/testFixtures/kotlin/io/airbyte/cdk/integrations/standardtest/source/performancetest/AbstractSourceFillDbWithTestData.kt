/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source.performancetest

import io.airbyte.cdk.db.Database
import java.util.*
import java.util.stream.Stream
import org.jooq.DSLContext
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** This abstract class contains common methods for Fill Db scripts. */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
abstract class AbstractSourceFillDbWithTestData : AbstractSourceBasePerformanceTest() {
    /**
     * Setup the test database. All tables and data described in the registered tests will be put
     * there.
     *
     * @return configured test database
     * @throws Exception
     * - might throw any exception during initialization.
     */
    @Throws(Exception::class) protected abstract fun setupDatabase(dbName: String?): Database

    /**
     * The test added test data to a new DB. 1. Set DB creds in static variables above 2. Set
     * desired number for streams, coolumns and records 3. Run the test
     */
    @Disabled
    @ParameterizedTest
    @MethodSource("provideParameters")
    @Throws(Exception::class)
    fun addTestData(
        dbName: String?,
        schemaName: String?,
        numberOfDummyRecords: Int,
        numberOfBatches: Int,
        numberOfColumns: Int,
        numberOfStreams: Int
    ) {
        val database = setupDatabase(dbName)

        database.query<Any?> { ctx: DSLContext ->
            for (currentSteamNumber in 0 until numberOfStreams) {
                val currentTableName = String.format(testStreamNameTemplate, currentSteamNumber)

                ctx.fetch(prepareCreateTableQuery(schemaName, numberOfColumns, currentTableName))
                for (i in 0 until numberOfBatches) {
                    val insertQueryTemplate =
                        prepareInsertQueryTemplate(
                            schemaName,
                            i,
                            numberOfColumns,
                            numberOfDummyRecords
                        )
                    ctx.fetch(String.format(insertQueryTemplate, currentTableName))
                }

                c.info("Finished processing for stream $currentSteamNumber")
            }
            null
        }
    }

    /**
     * This is a data provider for fill DB script,, Each argument's group would be ran as a separate
     * test. Set the "testArgs" in test class of your DB in @BeforeTest method.
     *
     * 1st arg - a name of DB that will be used in jdbc connection string. 2nd arg - a schemaName
     * that will be ised as a NameSpace in Configured Airbyte Catalog. 3rd arg - a number of
     * expected records retrieved in each stream. 4th arg - a number of columns in each stream\table
     * that will be use for Airbyte Cataloq configuration 5th arg - a number of streams to read in
     * configured airbyte Catalog. Each stream\table in DB should be names like "test_0",
     * "test_1",..., test_n.
     *
     * Stream.of( Arguments.of("your_db_name", "your_schema_name", 100, 2, 240, 1000) );
     */
    protected abstract fun provideParameters(): Stream<Arguments?>?

    protected fun prepareCreateTableQuery(
        dbSchemaName: String?,
        numberOfColumns: Int,
        currentTableName: String?
    ): String {
        val sj = StringJoiner(",")
        for (i in 0 until numberOfColumns) {
            sj.add(String.format(" %s%s %s", testColumnName, i, TEST_DB_FIELD_TYPE))
        }

        return String.format(
            CREATE_DB_TABLE_TEMPLATE,
            dbSchemaName,
            currentTableName,
            sj.toString()
        )
    }

    protected fun prepareInsertQueryTemplate(
        dbSchemaName: String?,
        batchNumber: Int,
        numberOfColumns: Int,
        recordsNumber: Int
    ): String {
        val fieldsNames = StringJoiner(",")
        fieldsNames.add("id")

        val baseInsertQuery = StringJoiner(",")
        baseInsertQuery.add("id_placeholder")

        for (i in 0 until numberOfColumns) {
            fieldsNames.add(testColumnName + i)
            baseInsertQuery.add(TEST_VALUE_TEMPLATE_POSTGRES)
        }

        val insertGroupValuesJoiner = StringJoiner(",")

        val batchMessages = batchNumber * 100

        for (currentRecordNumber in batchMessages until recordsNumber + batchMessages) {
            insertGroupValuesJoiner.add(
                "(" +
                    baseInsertQuery
                        .toString()
                        .replace("id_placeholder".toRegex(), currentRecordNumber.toString()) +
                    ")"
            )
        }

        return String.format(
            INSERT_INTO_DB_TABLE_QUERY_TEMPLATE,
            dbSchemaName,
            "%s",
            fieldsNames.toString(),
            insertGroupValuesJoiner.toString()
        )
    }

    companion object {
        private const val CREATE_DB_TABLE_TEMPLATE =
            "CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, %s)"
        private const val INSERT_INTO_DB_TABLE_QUERY_TEMPLATE = "INSERT INTO %s.%s (%s) VALUES %s"
        private const val TEST_DB_FIELD_TYPE = "varchar(10)"

        protected val c: Logger =
            LoggerFactory.getLogger(AbstractSourceFillDbWithTestData::class.java)
        private const val TEST_VALUE_TEMPLATE_POSTGRES = "\'Value id_placeholder\'"
    }
}
