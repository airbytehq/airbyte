/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.google.errorprone.annotations.MustBeClosed
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.db.jdbc.streaming.JdbcStreamingQueryConfig
import io.airbyte.commons.functional.CheckedFunction
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.*
import java.util.Spliterators.AbstractSpliterator
import java.util.function.Consumer
import java.util.function.Supplier
import java.util.stream.Stream
import java.util.stream.StreamSupport
import javax.sql.DataSource

private val LOGGER = KotlinLogging.logger {}

/**
 * This database allows a developer to specify a [JdbcStreamingQueryConfig]. This allows the
 * developer to specify the correct configuration in order for a [PreparedStatement] to execute as
 * in a streaming / chunked manner.
 */
class StreamingJdbcDatabase(
    dataSource: DataSource,
    sourceOperations: JdbcCompatibleSourceOperations<*>?,
    private val streamingQueryConfigProvider: Supplier<JdbcStreamingQueryConfig>
) : DefaultJdbcDatabase(dataSource, sourceOperations) {
    /**
     * Assuming that the [JdbcStreamingQueryConfig] is configured correctly for the JDBC driver
     * being used, this method will return data in streaming / chunked fashion. Review the provided
     * [JdbcStreamingQueryConfig] to understand the size of these chunks. If the entire stream is
     * consumed the database connection will be closed automatically and the caller need not call
     * close on the returned stream. This query (and the first chunk) are fetched immediately.
     * Subsequent chunks will not be pulled until the first chunk is consumed.
     *
     * @param statementCreator create a [PreparedStatement] from a [Connection].
     * @param recordTransform transform each record of that result set into the desired type. do NOT
     * just pass the [ResultSet] through. it is a stateful object will not be accessible if returned
     * from recordTransform.
     * @param <T> type that each record will be mapped to.
     * @return Result of the query mapped to a stream. This stream must be closed!
     * @throws SQLException SQL related exceptions. </T>
     */
    @MustBeClosed
    @Throws(SQLException::class)
    override fun <T> unsafeQuery(
        statementCreator: CheckedFunction<Connection, PreparedStatement, SQLException>,
        recordTransform: CheckedFunction<ResultSet, T, SQLException>
    ): Stream<T> {
        try {
            val connection = dataSource.connection
            val statement = statementCreator.apply(connection)
            val streamingConfig = streamingQueryConfigProvider.get()
            streamingConfig.initialize(connection, statement)
            return toUnsafeStream(statement.executeQuery(), recordTransform, streamingConfig)
                .onClose {
                    try {
                        if (!connection.autoCommit) {
                            connection.autoCommit = true
                        }
                        connection.close()
                        if (isStreamFailed) {
                            throw RuntimeException(streamException)
                        }
                    } catch (e: SQLException) {
                        throw RuntimeException(e)
                    }
                }
        } catch (e: SQLException) {
            throw RuntimeException(e)
        }
    }

    /**
     * This method differs from [DefaultJdbcDatabase.toUnsafeStream] in that it takes a streaming
     * config that adjusts the fetch size dynamically according to sampled row size.
     */
    protected fun <T> toUnsafeStream(
        resultSet: ResultSet,
        mapper: CheckedFunction<ResultSet, T, SQLException>,
        streamingConfig: JdbcStreamingQueryConfig
    ): Stream<T> {
        return StreamSupport.stream(
            object : AbstractSpliterator<T>(Long.MAX_VALUE, ORDERED) {
                override fun tryAdvance(action: Consumer<in T>): Boolean {
                    try {
                        if (!resultSet.next()) {
                            resultSet.close()
                            return false
                        }
                        val dataRow = mapper.apply(resultSet)
                        streamingConfig.accept(resultSet, dataRow)
                        action.accept(dataRow)
                        return true
                    } catch (e: SQLException) {
                        LOGGER.error { "SQLState: ${e.sqlState}, Message: ${e.message}" }
                        streamException = e
                        isStreamFailed = true
                        throw RuntimeException(e)
                    }
                }
            },
            false
        )
    }
}
