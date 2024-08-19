/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.errorprone.annotations.MustBeClosed
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.db.SqlDatabase
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.functional.CheckedFunction
import java.sql.*
import java.util.Spliterators.AbstractSpliterator
import java.util.function.Consumer
import java.util.function.Function
import java.util.stream.Stream
import java.util.stream.StreamSupport
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** Database object for interacting with a JDBC connection. */
abstract class JdbcDatabase(protected val sourceOperations: JdbcCompatibleSourceOperations<*>?) :
    SqlDatabase() {
    protected var streamException: Exception? = null
    protected var isStreamFailed: Boolean = false

    /**
     * Execute a database query.
     *
     * @param query the query to execute against the database.
     * @throws SQLException SQL related exceptions.
     */
    @Throws(SQLException::class)
    abstract fun execute(query: CheckedConsumer<Connection, SQLException>)

    /**
     * We can't define a default parameter in the method below because "An overriding function is
     * not allowed to specify default values for its parameters" in kotlin And the interface could
     * have a default parameter, but is not allowed an @JvmOverload because it's abstract. So for
     * java compat, we have 2 functions, the same way we would in java
     */
    override fun execute(sql: String?) {
        execute(sql, true)
    }

    @Throws(SQLException::class)
    fun execute(sql: String?, logStatements: Boolean) {
        execute { connection: Connection ->
            if (logStatements) {
                LOGGER.info("executing statement: $sql")
            }
            connection.createStatement().execute(sql)
            if (logStatements) {
                LOGGER.info("statement successfully executed")
            }
        }
    }

    @Throws(SQLException::class)
    fun executeWithinTransaction(queries: List<String>, logStatements: Boolean = true) {
        execute { connection: Connection ->
            connection.autoCommit = false
            for (s in queries) {
                if (logStatements) {
                    LOGGER.info("executing query within transaction: $s")
                }
                connection.createStatement().execute(s)
                if (logStatements) {
                    LOGGER.info("done executing query within transaction: $s")
                }
            }
            connection.commit()
            connection.autoCommit = true
        }
    }

    /**
     * Use a connection to create a [ResultSet] and map it into a list. The entire [ResultSet] will
     * be buffered in memory before the list is returned. The caller does not need to worry about
     * closing any database resources.
     *
     * @param query execute a query using a [Connection] to get a [ResultSet].
     * @param recordTransform transform each record of that result set into the desired type. do NOT
     * just pass the [ResultSet] through. it is a stateful object will not be accessible if returned
     * from recordTransform.
     * @param <T> type that each record will be mapped to.
     * @return Result of the query mapped to a list.
     * @throws SQLException SQL related exceptions. </T>
     */
    @Throws(SQLException::class)
    abstract fun <T> bufferedResultSetQuery(
        query: CheckedFunction<Connection, ResultSet, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): List<T>

    /**
     * Use a connection to create a [ResultSet] and map it into a stream. You CANNOT assume that
     * data will be returned from this method before the entire [ResultSet] is buffered in memory.
     * Review the implementation of the database's JDBC driver or use the StreamingJdbcDriver if you
     * need this guarantee. It is "unsafe" because the caller should close the returned stream to
     * release the database connection. Otherwise, there will be a connection leak.
     *
     * @param query execute a query using a [Connection] to get a [ResultSet].
     * @param recordTransform transform each record of that result set into the desired type. do NOT
     * just pass the [ResultSet] through. it is a stateful object will not be accessible if returned
     * from recordTransform.
     * @param <T> type that each record will be mapped to.
     * @return Result of the query mapped to a stream.
     * @throws SQLException SQL related exceptions. </T>
     */
    @MustBeClosed
    @Throws(SQLException::class)
    abstract fun <T> unsafeResultSetQuery(
        query: CheckedFunction<Connection, ResultSet, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): Stream<T>

    /**
     * String query is a common use case for [JdbcDatabase.unsafeResultSetQuery]. So this method is
     * created as syntactic sugar.
     */
    @Throws(SQLException::class)
    fun queryStrings(
        query: CheckedFunction<Connection, ResultSet, SQLException>,
        recordTransform: CheckedFunction<ResultSet, String, SQLException>
    ): List<String> {
        unsafeResultSetQuery(query, recordTransform).use { stream ->
            return stream.toList()
        }
    }

    /**
     * Use a connection to create a [PreparedStatement] and map it into a stream. You CANNOT assume
     * that data will be returned from this method before the entire [ResultSet] is buffered in
     * memory. Review the implementation of the database's JDBC driver or use the
     * StreamingJdbcDriver if you need this guarantee. It is "unsafe" because the caller should
     * close the returned stream to release the database connection. Otherwise, there will be a
     * connection leak.
     *
     * @paramstatementCreator create a [PreparedStatement] from a [Connection].
     * @param recordTransform transform each record of that result set into the desired type. do NOT
     * just pass the [ResultSet] through. it is a stateful object will not be accessible if returned
     * from recordTransform.
     * @param <T> type that each record will be mapped to.
     * @return Result of the query mapped to a stream.void execute(String sql)
     * @throws SQLException SQL related exceptions. </T>
     */
    @MustBeClosed
    @Throws(SQLException::class)
    abstract fun <T> unsafeQuery(
        statementCreator: CheckedFunction<Connection, PreparedStatement, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): Stream<T>

    /**
     * Json query is a common use case for [JdbcDatabase.unsafeQuery]. So this method is created as
     * syntactic sugar.
     */
    @Throws(SQLException::class)
    fun queryJsons(
        statementCreator: CheckedFunction<Connection, PreparedStatement, SQLException>,
        recordTransform: CheckedFunction<ResultSet, JsonNode, SQLException>
    ): List<JsonNode> {
        unsafeQuery(statementCreator, recordTransform).use { stream ->
            return stream.toList()
        }
    }

    @Throws(SQLException::class)
    fun queryInt(sql: String, vararg params: String): Int {
        unsafeQuery(
                { c: Connection -> getPreparedStatement(sql, params, c) },
                { rs: ResultSet -> rs.getInt(1) }
            )
            .use { stream ->
                return stream.findFirst().get()
            }
    }

    @Throws(SQLException::class)
    fun queryBoolean(sql: String, vararg params: String): Boolean {
        unsafeQuery(
                { c: Connection -> getPreparedStatement(sql, params, c) },
                { rs: ResultSet -> rs.getBoolean(1) }
            )
            .use { stream ->
                return stream.findFirst().get()
            }
    }

    /**
     * It is "unsafe" because the caller must manually close the returned stream. Otherwise, there
     * will be a database connection leak.
     */
    @MustBeClosed
    @Throws(SQLException::class)
    override fun unsafeQuery(sql: String?, vararg params: String): Stream<JsonNode> {
        return unsafeQuery(
            { connection: Connection ->
                val statement = connection.prepareStatement(sql)
                var i = 1
                for (param in params) {
                    statement.setString(i, param)
                    ++i
                }
                statement
            },
            { queryResult: ResultSet -> sourceOperations!!.rowToJson(queryResult) }
        )
    }

    /**
     * Json query is a common use case for [JdbcDatabase.unsafeQuery]. So this method is created as
     * syntactic sugar.
     */
    @Throws(SQLException::class)
    fun queryJsons(sql: String?, vararg params: String): List<JsonNode> {
        unsafeQuery(sql, *params).use { stream ->
            return stream.toList()
        }
    }

    @Throws(SQLException::class)
    fun queryMetadata(sql: String, vararg params: String): ResultSetMetaData? {
        unsafeQuery(
                { c: Connection -> getPreparedStatement(sql, params, c) },
                { obj: ResultSet -> obj.metaData },
            )
            .use { q ->
                return q.findFirst().orElse(null)
            }
    }

    @get:Throws(SQLException::class) abstract val metaData: DatabaseMetaData

    @Throws(SQLException::class)
    abstract fun <T> executeMetadataQuery(query: Function<DatabaseMetaData, T>): T

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(JdbcDatabase::class.java)
        /**
         * Map records returned in a result set. It is an "unsafe" stream because the stream must be
         * manually closed. Otherwise, there will be a database connection leak.
         *
         * @param resultSet the result set
         * @param mapper function to make each record of the result set
         * @param <T> type that each record will be mapped to
         * @return stream of records that the result set is mapped to. </T>
         */
        @JvmStatic
        @MustBeClosed
        fun <T> toUnsafeStream(
            resultSet: ResultSet,
            mapper: CheckedFunction<ResultSet, T, SQLException>
        ): Stream<T> {
            return StreamSupport.stream(
                object : AbstractSpliterator<T>(Long.MAX_VALUE, ORDERED) {
                    override fun tryAdvance(action: Consumer<in T>): Boolean {
                        try {
                            if (!resultSet.next()) {
                                resultSet.close()
                                return false
                            }
                            action.accept(mapper.apply(resultSet))
                            return true
                        } catch (e: SQLException) {
                            throw RuntimeException(e)
                        }
                    }
                },
                false
            )
        }

        @Throws(SQLException::class)
        private fun getPreparedStatement(
            sql: String,
            params: Array<out String>,
            c: Connection
        ): PreparedStatement {
            val statement = c.prepareStatement(sql)
            var i = 1
            for (param in params) {
                statement.setString(i, param)
                i++
            }
            return statement
        }
    }
}
