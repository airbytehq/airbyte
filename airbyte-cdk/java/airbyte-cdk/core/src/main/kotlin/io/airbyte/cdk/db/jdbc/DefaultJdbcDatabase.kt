/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.google.errorprone.annotations.MustBeClosed
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.functional.CheckedFunction
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.*
import java.util.*
import java.util.function.Function
import java.util.stream.Stream
import javax.sql.DataSource

private val LOGGER = KotlinLogging.logger {}
/**
 * Database object for interacting with a JDBC connection. Can be used for any JDBC compliant db.
 */
open class DefaultJdbcDatabase
@JvmOverloads
constructor(
    protected val dataSource: DataSource,
    sourceOperations: JdbcCompatibleSourceOperations<*>? = JdbcUtils.defaultSourceOperations
) : JdbcDatabase(sourceOperations) {
    @Throws(SQLException::class)
    override fun execute(query: CheckedConsumer<Connection, SQLException>) {
        dataSource.connection.use { connection -> query.accept(connection) }
    }

    @Throws(SQLException::class)
    override fun <T> bufferedResultSetQuery(
        query: CheckedFunction<Connection, ResultSet, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): List<T> {
        dataSource.connection.use { connection ->
            toUnsafeStream<T>(query.apply(connection), recordTransform).use { results ->
                return results.toList()
            }
        }
    }

    @MustBeClosed
    @Throws(SQLException::class)
    override fun <T> unsafeResultSetQuery(
        query: CheckedFunction<Connection, ResultSet, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): Stream<T> {
        val connection = dataSource.connection
        return JdbcDatabase.Companion.toUnsafeStream<T>(query.apply(connection), recordTransform)
            .onClose {
                try {
                    connection.close()
                } catch (e: SQLException) {
                    throw RuntimeException(e)
                }
            }
    }

    @get:Throws(SQLException::class)
    override val metaData: DatabaseMetaData
        get() {
            try {
                dataSource.connection.use { connection ->
                    val metaData = connection.metaData
                    return metaData
                }
            } catch (e: SQLException) {
                // Some databases like Redshift will have null cause
                if (Objects.isNull(e.cause) || e.cause !is SQLException) {
                    throw ConnectionErrorException(e.sqlState, e.errorCode, e.message, e)
                } else {
                    val cause = e.cause as SQLException?
                    throw ConnectionErrorException(e.sqlState, cause!!.errorCode, cause.message, e)
                }
            }
        }

    override fun <T> executeMetadataQuery(query: Function<DatabaseMetaData, T>): T {
        try {
            dataSource.connection.use { connection ->
                val metaData = connection.metaData
                return query.apply(metaData)
            }
        } catch (e: SQLException) {
            // Some databases like Redshift will have null cause
            if (Objects.isNull(e.cause) || e.cause !is SQLException) {
                throw ConnectionErrorException(e.sqlState, e.errorCode, e.message, e)
            } else {
                val cause = e.cause as SQLException?
                throw ConnectionErrorException(e.sqlState, cause!!.errorCode, cause.message, e)
            }
        }
    }

    /**
     * You CANNOT assume that data will be returned from this method before the entire [ResultSet]
     * is buffered in memory. Review the implementation of the database's JDBC driver or use the
     * StreamingJdbcDriver if you need this guarantee. The caller should close the returned stream
     * to release the database connection.
     *
     * @param statementCreator create a [PreparedStatement] from a [Connection].
     * @param recordTransform transform each record of that result set into the desired type. do NOT
     * just pass the [ResultSet] through. it is a stateful object will not be accessible if returned
     * from recordTransform.
     * @param <T> type that each record will be mapped to.
     * @return Result of the query mapped to a stream.
     * @throws SQLException SQL related exceptions. </T>
     */
    @MustBeClosed
    @Throws(SQLException::class)
    override fun <T> unsafeQuery(
        statementCreator: CheckedFunction<Connection, PreparedStatement, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): Stream<T> {
        val connection = dataSource.connection
        return JdbcDatabase.Companion.toUnsafeStream<T>(
                statementCreator.apply(connection).executeQuery(),
                recordTransform
            )
            .onClose(
                Runnable {
                    try {
                        LOGGER.info { "closing connection" }
                        connection.close()
                    } catch (e: SQLException) {
                        throw RuntimeException(e)
                    }
                }
            )
    }
}
