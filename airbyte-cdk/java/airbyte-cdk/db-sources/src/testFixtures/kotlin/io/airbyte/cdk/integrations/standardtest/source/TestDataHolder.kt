/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source

import io.airbyte.protocol.models.JsonSchemaType
import java.util.*

class TestDataHolder
internal constructor(
    val sourceType: String?,
    val airbyteType: JsonSchemaType,
    val values: List<String>,
    val expectedValues: MutableList<String?>,
    private val createTablePatternSql: String,
    private val insertPatternSql: String,
    private val fullSourceDataType: String?
) {
    var nameSpace: String? = null
    private var testNumber: Int = 0
    private var idColumnName: String? = null
    private var testColumnName: String? = null

    var declarationLocation: String = ""
        private set

    class TestDataHolderBuilder internal constructor() {
        private var sourceType: String? = null
        private lateinit var airbyteType: JsonSchemaType
        private val values: MutableList<String> = ArrayList()
        private val expectedValues: MutableList<String?> = ArrayList()
        private var createTablePatternSql: String
        private var insertPatternSql: String
        private var fullSourceDataType: String? = null

        init {
            this.createTablePatternSql = DEFAULT_CREATE_TABLE_SQL
            this.insertPatternSql = DEFAULT_INSERT_SQL
        }

        /**
         * The name of the source data type. Duplicates by name will be tested independently from
         * each others. Note that this name will be used for connector setup and table creation. If
         * source syntax requires more details (E.g. "varchar" type requires length "varchar(50)"),
         * you can additionally set custom data type syntax by
         * [TestDataHolderBuilder.fullSourceDataType] method.
         *
         * @param sourceType source data type name
         * @return builder
         */
        fun sourceType(sourceType: String?): TestDataHolderBuilder {
            this.sourceType = sourceType
            if (fullSourceDataType == null) fullSourceDataType = sourceType
            return this
        }

        /**
         * corresponding Airbyte data type. It requires for proper configuration
         * [ConfiguredAirbyteStream]
         *
         * @param airbyteType Airbyte data type
         * @return builder
         */
        fun airbyteType(airbyteType: JsonSchemaType): TestDataHolderBuilder {
            this.airbyteType = airbyteType
            return this
        }

        /**
         * Set custom the create table script pattern. Use it if you source uses untypical table
         * creation sql. Default patter described [.DEFAULT_CREATE_TABLE_SQL] Note! The patter
         * should contain four String place holders for the: - namespace.table name (as one
         * placeholder together) - id column name - test column name - test column data type
         *
         * @param createTablePatternSql creation table sql pattern
         * @return builder
         */
        fun createTablePatternSql(createTablePatternSql: String): TestDataHolderBuilder {
            this.createTablePatternSql = createTablePatternSql
            return this
        }

        /**
         * Set custom the insert record script pattern. Use it if you source uses untypical insert
         * record sql. Default patter described [.DEFAULT_INSERT_SQL] Note! The patter should
         * contains two String place holders for the table name and value.
         *
         * @param insertPatternSql creation table sql pattern
         * @return builder
         */
        fun insertPatternSql(insertPatternSql: String): TestDataHolderBuilder {
            this.insertPatternSql = insertPatternSql
            return this
        }

        /**
         * Allows to set extended data type for the table creation. E.g. The "varchar" type requires
         * in MySQL requires length. In this case fullSourceDataType will be "varchar(50)".
         *
         * @param fullSourceDataType actual string for the column data type description
         * @return builder
         */
        fun fullSourceDataType(fullSourceDataType: String?): TestDataHolderBuilder {
            this.fullSourceDataType = fullSourceDataType
            return this
        }

        /**
         * Adds value(s) to the scope of a corresponding test. The values will be inserted into the
         * created table. Note! The value will be inserted into the insert script without any
         * transformations. Make sure that the value is in line with the source syntax.
         *
         * @param insertValue test value
         * @return builder
         */
        fun addInsertValues(vararg insertValue: String): TestDataHolderBuilder {
            values.addAll(Arrays.asList(*insertValue))
            return this
        }

        /**
         * Adds expected value(s) to the test scope. If you add at least one value, it will check
         * that all values are provided by corresponding streamer.
         *
         * @param expectedValue value which should be provided by a streamer
         * @return builder
         */
        fun addExpectedValues(vararg expectedValue: String?): TestDataHolderBuilder {
            expectedValues.addAll(Arrays.asList(*expectedValue))
            return this
        }

        /**
         * Add NULL value to the expected value list. If you need to add only one value and it's
         * NULL, you have to use this method instead of [.addExpectedValues]
         *
         * @return builder
         */
        fun addNullExpectedValue(): TestDataHolderBuilder {
            expectedValues.add(null)
            return this
        }

        fun build(): TestDataHolder {
            return TestDataHolder(
                sourceType,
                airbyteType,
                values,
                expectedValues,
                createTablePatternSql,
                insertPatternSql,
                fullSourceDataType
            )
        }
    }

    fun setTestNumber(testNumber: Int) {
        this.testNumber = testNumber
    }

    fun setIdColumnName(idColumnName: String?) {
        this.idColumnName = idColumnName
    }

    fun setTestColumnName(testColumnName: String?) {
        this.testColumnName = testColumnName
    }

    val nameWithTestPrefix: String
        get() = // source type may include space (e.g. "character varying")
        nameSpace + "_" + testNumber + "_" + sourceType!!.replace("\\s".toRegex(), "_")

    val createSqlQuery: String
        get() =
            String.format(
                createTablePatternSql,
                (if (nameSpace != null) "$nameSpace." else "") + this.nameWithTestPrefix,
                idColumnName,
                testColumnName,
                fullSourceDataType
            )

    fun setDeclarationLocation(declarationLocation: Array<StackTraceElement>) {
        this.declarationLocation = Arrays.asList(*declarationLocation).subList(2, 3).toString()
    }

    val insertSqlQueries: List<String>
        get() {
            val insertSqls: MutableList<String> = ArrayList()
            var rowId = 1
            for (value in values) {
                insertSqls.add(
                    String.format(
                        insertPatternSql,
                        (if (nameSpace != null) "$nameSpace." else "") + this.nameWithTestPrefix,
                        rowId++,
                        value
                    )
                )
            }
            return insertSqls
        }

    companion object {
        private const val DEFAULT_CREATE_TABLE_SQL =
            "CREATE TABLE %1\$s(%2\$s INTEGER PRIMARY KEY, %3\$s %4\$s)"
        private const val DEFAULT_INSERT_SQL = "INSERT INTO %1\$s VALUES (%2\$s, %3\$s)"

        /**
         * The builder allows to setup any comprehensive data type test.
         *
         * @return builder for setup comprehensive test
         */
        @JvmStatic
        fun builder(): TestDataHolderBuilder {
            return TestDataHolderBuilder()
        }
    }
}
