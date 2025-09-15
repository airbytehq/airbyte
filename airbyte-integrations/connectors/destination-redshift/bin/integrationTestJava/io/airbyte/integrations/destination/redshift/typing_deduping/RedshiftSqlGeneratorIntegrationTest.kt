/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.jdbc.DateTimeConverter.convertToTimeWithTimezone
import io.airbyte.cdk.db.jdbc.DateTimeConverter.convertToTimestamp
import io.airbyte.cdk.db.jdbc.DateTimeConverter.convertToTimestampWithTimezone
import io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.cdk.db.jdbc.JdbcUtils.DATABASE_KEY
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.deserializeExact
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.destination.redshift.RedshiftDestination
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer
import java.nio.file.Files
import java.nio.file.Path
import java.sql.ResultSet
import java.sql.SQLException
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.util.List
import java.util.Locale
import javax.sql.DataSource
import org.jooq.DSLContext
import org.jooq.DataType
import org.jooq.Field
import org.jooq.SQLDialect
import org.jooq.conf.ParamType
import org.jooq.conf.Settings
import org.jooq.impl.DSL
import org.jooq.impl.DefaultDataType
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class RedshiftSqlGeneratorIntegrationTest : JdbcSqlGeneratorIntegrationTest<RedshiftState>() {
    override val supportsSafeCast: Boolean
        get() = true

    /**
     * Redshift's JDBC driver doesn't map certain data types onto [java.sql.JDBCType] usefully. This
     * class adds special handling for those types.
     */
    class RedshiftSourceOperations : JdbcSourceOperations() {
        @Throws(SQLException::class)
        override fun copyToJsonField(resultSet: ResultSet, colIndex: Int, json: ObjectNode) {
            val columnName = resultSet.metaData.getColumnName(colIndex)
            val columnTypeName =
                resultSet.metaData.getColumnTypeName(colIndex).lowercase(Locale.getDefault())

            when (columnTypeName) {
                "super" ->
                    json.set<JsonNode>(columnName, deserializeExact(resultSet.getString(colIndex)))
                "timetz" -> putTimeWithTimezone(json, columnName, resultSet, colIndex)
                "timestamptz" -> putTimestampWithTimezone(json, columnName, resultSet, colIndex)
                else -> super.copyToJsonField(resultSet, colIndex, json)
            }
        }

        @Throws(SQLException::class)
        override fun putTimeWithTimezone(
            node: ObjectNode,
            columnName: String?,
            resultSet: ResultSet,
            index: Int
        ) {
            val offsetTime =
                resultSet.getTimestamp(index).toInstant().atOffset(ZoneOffset.UTC).toOffsetTime()
            node.put(columnName, convertToTimeWithTimezone(offsetTime))
        }

        @Throws(SQLException::class)
        override fun putTime(
            node: ObjectNode,
            columnName: String?,
            resultSet: ResultSet,
            index: Int
        ) {
            putJavaSQLTime(node, columnName, resultSet, index)
        }

        @Throws(SQLException::class)
        override fun putTimestampWithTimezone(
            node: ObjectNode,
            columnName: String?,
            resultSet: ResultSet,
            index: Int
        ) {
            // The superclass implementation tries to fetch a OffsetDateTime, which fails.
            try {
                super.putTimestampWithTimezone(node, columnName, resultSet, index)
            } catch (e: Exception) {
                val instant = resultSet.getTimestamp(index).toInstant()
                node.put(columnName, convertToTimestampWithTimezone(instant))
            }
        }

        // Base class is converting to Instant which assumes the base timezone is UTC and resolves
        // the local
        // value to system's timezone.
        @Throws(SQLException::class)
        override fun putTimestamp(
            node: ObjectNode,
            columnName: String?,
            resultSet: ResultSet,
            index: Int
        ) {
            try {
                node.put(
                    columnName,
                    convertToTimestamp(getObject(resultSet, index, LocalDateTime::class.java))
                )
            } catch (e: Exception) {
                val localDateTime = resultSet.getTimestamp(index).toLocalDateTime()
                node.put(columnName, convertToTimestamp(localDateTime))
            }
        }
    }

    override val sqlGenerator: JdbcSqlGenerator
        get() =
            object : RedshiftSqlGenerator(RedshiftSQLNameTransformer(), false) {
                override val dslContext: DSLContext
                    // Override only for tests to print formatted SQL. The actual implementation
                    // should use unformatted
                    get() = DSL.using(dialect, Settings().withRenderFormatted(true))
            }

    override val destinationHandler: DestinationHandler<RedshiftState>
        get() = RedshiftDestinationHandler(databaseName, Companion.database!!, namespace)

    override val database: JdbcDatabase
        get() = Companion.database

    override val structType: DataType<*>
        get() = DefaultDataType(null, String::class.java, "super")

    override val sqlDialect: SQLDialect
        get() = SQLDialect.POSTGRES

    override fun toJsonValue(valueAsString: String?): Field<*> {
        return DSL.function(
            "JSON_PARSE",
            String::class.java,
            DSL.`val`(escapeStringLiteral(valueAsString))
        )
    }

    @Test
    @Throws(Exception::class)
    override fun testCreateTableIncremental() {
        val sql = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(sql)
        val initialStatuses = destinationHandler.gatherInitialState(List.of(incrementalDedupStream))
        Assertions.assertEquals(1, initialStatuses.size)
        val initialStatus = initialStatuses.first()
        Assertions.assertTrue(initialStatus.isFinalTablePresent)
        Assertions.assertFalse(initialStatus.isSchemaMismatch)
        // TODO assert on table clustering, etc.
    }

    /** Verify that we correctly DROP...CASCADE the final table when cascadeDrop is enabled. */
    @Test
    @Throws(Exception::class)
    fun testCascadeDropEnabled() {
        // Explicitly create a sqlgenerator with cascadeDrop=true
        val generator = RedshiftSqlGenerator(RedshiftSQLNameTransformer(), true)
        // Create a table, then create a view referencing it
        destinationHandler.execute(generator.createTable(incrementalAppendStream, "", false))
        Companion.database!!.execute(
            DSL.createView(
                    DSL.quotedName(incrementalAppendStream.id.finalNamespace, "example_view")
                )
                .`as`(
                    DSL.select()
                        .from(
                            DSL.quotedName(
                                incrementalAppendStream.id.finalNamespace,
                                incrementalAppendStream.id.finalName
                            )
                        )
                )
                .getSQL(ParamType.INLINED)
        )
        // Create a "soft reset" table
        destinationHandler.execute(
            generator.createTable(incrementalDedupStream, "_soft_reset", false)
        )

        // Overwriting the first table with the second table should succeed.
        Assertions.assertDoesNotThrow {
            destinationHandler.execute(
                generator.overwriteFinalTable(incrementalDedupStream.id, "_soft_reset")
            )
        }
    }

    @Test
    @Throws(Exception::class)
    fun testCascadeDropDisabled() {
        // Explicitly create a sqlgenerator with cascadeDrop=false
        val generator = RedshiftSqlGenerator(RedshiftSQLNameTransformer(), false)
        // Create a table, then create a view referencing it
        destinationHandler.execute(generator.createTable(incrementalAppendStream, "", false))
        Companion.database!!.execute(
            DSL.createView(
                    DSL.quotedName(incrementalAppendStream.id.finalNamespace, "example_view")
                )
                .`as`(
                    DSL.select()
                        .from(
                            DSL.quotedName(
                                incrementalAppendStream.id.finalNamespace,
                                incrementalAppendStream.id.finalName
                            )
                        )
                )
                .getSQL(ParamType.INLINED)
        )
        // Create a "soft reset" table
        destinationHandler.execute(
            generator.createTable(incrementalDedupStream, "_soft_reset", false)
        )

        // Overwriting the first table with the second table should fal with a configurationError.
        val t: Throwable =
            Assertions.assertThrowsExactly(ConfigErrorException::class.java) {
                destinationHandler.execute(
                    generator.overwriteFinalTable(incrementalDedupStream.id, "_soft_reset")
                )
            }
        Assertions.assertTrue(
            t.message ==
                "Failed to drop table without the CASCADE option. Consider changing the drop_cascade configuration parameter"
        )
    }

    companion object {
        private lateinit var dataSource: DataSource
        private lateinit var database: JdbcDatabase
        private lateinit var databaseName: String

        @JvmStatic
        @BeforeAll
        @Throws(Exception::class)
        fun setupJdbcDatasource() {
            val rawConfig = Files.readString(Path.of("secrets/1s1t_config.json"))
            val config = deserialize(rawConfig)
            // TODO: Existing in AbstractJdbcDestination, pull out to a util file
            databaseName = config.get(DATABASE_KEY).asText()
            // TODO: Its sad to instantiate unneeded dependency to construct database and
            // datsources. pull it to
            // static methods.
            val insertDestination = RedshiftDestination()
            dataSource = insertDestination.getDataSource(config)
            database = insertDestination.getDatabase(dataSource, RedshiftSourceOperations())
        }

        @JvmStatic
        @AfterAll
        @Throws(Exception::class)
        fun teardownRedshift() {
            close(dataSource)
        }

        fun escapeStringLiteral(str: String?): String? {
            return str?.replace("\\", "\\\\")
        }
    }
}
