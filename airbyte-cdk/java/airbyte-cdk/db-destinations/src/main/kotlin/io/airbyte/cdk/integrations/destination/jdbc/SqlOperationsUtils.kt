/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.google.common.annotations.VisibleForTesting
import com.google.common.collect.Iterables
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag.isDestinationV2
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.functional.CheckedConsumer
import java.sql.Connection
import java.sql.SQLException
import java.sql.Timestamp
import java.time.Instant
import java.util.*
import java.util.function.Supplier

object SqlOperationsUtils {
    /**
     * Inserts "raw" records in a single query. The purpose of helper to abstract away
     * database-specific SQL syntax from this query.
     *
     * @param insertQueryComponent the first line of the query e.g. INSERT INTO public.users (ab_id,
     * data, emitted_at)
     * @param recordQueryComponent query template for a full record e.g. (?, ?::jsonb ?)
     * @param jdbcDatabase jdbc database
     * @param records records to write
     * @throws SQLException exception
     */
    @JvmStatic
    @Throws(SQLException::class)
    fun insertRawRecordsInSingleQuery(
        insertQueryComponent: String?,
        recordQueryComponent: String?,
        jdbcDatabase: JdbcDatabase,
        records: List<PartialAirbyteMessage>
    ) {
        insertRawRecordsInSingleQuery(
            insertQueryComponent,
            recordQueryComponent,
            jdbcDatabase,
            records,
            { UUID.randomUUID() },
            true
        )
    }

    /**
     * Inserts "raw" records in a single query. The purpose of helper to abstract away
     * database-specific SQL syntax from this query.
     *
     * This version does not add a semicolon at the end of the INSERT statement.
     *
     * @param insertQueryComponent the first line of the query e.g. INSERT INTO public.users (ab_id,
     * data, emitted_at)
     * @param recordQueryComponent query template for a full record e.g. (?, ?::jsonb ?)
     * @param jdbcDatabase jdbc database
     * @param records records to write
     * @throws SQLException exception
     */
    @Throws(SQLException::class)
    fun insertRawRecordsInSingleQueryNoSem(
        insertQueryComponent: String?,
        recordQueryComponent: String?,
        jdbcDatabase: JdbcDatabase,
        records: List<PartialAirbyteMessage>
    ) {
        insertRawRecordsInSingleQuery(
            insertQueryComponent,
            recordQueryComponent,
            jdbcDatabase,
            records,
            { UUID.randomUUID() },
            false
        )
    }

    @VisibleForTesting
    @Throws(SQLException::class)
    fun insertRawRecordsInSingleQuery(
        insertQueryComponent: String?,
        recordQueryComponent: String?,
        jdbcDatabase: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        uuidSupplier: Supplier<UUID>,
        sem: Boolean
    ) {
        if (records.isEmpty()) {
            return
        }

        jdbcDatabase.execute(
            CheckedConsumer { connection: Connection ->

                // Strategy: We want to use PreparedStatement because it handles binding values to
                // the SQL query
                // (e.g. handling formatting timestamps). A PreparedStatement statement is created
                // by supplying the
                // full SQL string at creation time. Then subsequently specifying which values are
                // bound to the
                // string. Thus there will be two loops below.
                // 1) Loop over records to build the full string.
                // 2) Loop over the records and bind the appropriate values to the string.
                // We also partition the query to run on 10k records at a time, since some DBs set a
                // max limit on
                // how many records can be inserted at once
                // TODO(sherif) this should use a smarter, destination-aware partitioning scheme
                // instead of 10k by
                // default
                for (partition in Iterables.partition(records, 10000)) {
                    val sql = StringBuilder(insertQueryComponent)
                    partition.forEach { _ -> sql.append(recordQueryComponent) }
                    val s = sql.toString()
                    val s1 = s.substring(0, s.length - 2) + (if (sem) ";" else "")

                    connection.prepareStatement(s1).use { statement ->
                        // second loop: bind values to the SQL string.
                        // 1-indexed
                        var i = 1
                        for (message in partition) {
                            // Airbyte Raw ID
                            statement.setString(i, uuidSupplier.get().toString())
                            i++

                            // Message Data
                            statement.setString(i, message.serialized)
                            i++

                            // Extracted At
                            statement.setTimestamp(
                                i,
                                Timestamp.from(Instant.ofEpochMilli(message.record!!.emittedAt))
                            )
                            i++

                            if (isDestinationV2) {
                                // Loaded At
                                statement.setTimestamp(i, null)
                                i++
                            }
                        }
                        statement.execute()
                    }
                }
            }
        )
    }
}
