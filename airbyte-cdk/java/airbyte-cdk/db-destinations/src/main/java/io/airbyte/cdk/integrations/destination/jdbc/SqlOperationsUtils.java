/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Stream;

public class SqlOperationsUtils {

  /**
   * Inserts "raw" records in a single query. The purpose of helper to abstract away database-specific
   * SQL syntax from this query.
   *
   * @param insertQueryComponent the first line of the query e.g. INSERT INTO public.users (ab_id,
   *        data, emitted_at)
   * @param recordQueryComponent query template for a full record e.g. (?, ?::jsonb ?)
   * @param jdbcDatabase jdbc database
   * @param records records to write
   * @throws SQLException exception
   */
  public static void insertRawRecordsInSingleQuery(final String insertQueryComponent,
                                                   final String recordQueryComponent,
                                                   final JdbcDatabase jdbcDatabase,
                                                   final Stream<PartialAirbyteMessage> records)
      throws SQLException {
    insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, jdbcDatabase, records, UUID::randomUUID, true);
  }

  /**
   * Inserts "raw" records in a single query. The purpose of helper to abstract away database-specific
   * SQL syntax from this query.
   *
   * This version does not add a semicolon at the end of the INSERT statement.
   *
   * @param insertQueryComponent the first line of the query e.g. INSERT INTO public.users (ab_id,
   *        data, emitted_at)
   * @param recordQueryComponent query template for a full record e.g. (?, ?::jsonb ?)
   * @param jdbcDatabase jdbc database
   * @param records records to write
   * @throws SQLException exception
   */
  public static void insertRawRecordsInSingleQueryNoSem(final String insertQueryComponent,
                                                        final String recordQueryComponent,
                                                        final JdbcDatabase jdbcDatabase,
                                                        final Stream<PartialAirbyteMessage> records)
      throws SQLException {
    insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, jdbcDatabase, records, UUID::randomUUID, false);
  }

  @VisibleForTesting
  static void insertRawRecordsInSingleQuery(final String insertQueryComponent,
                                            final String recordQueryComponent,
                                            final JdbcDatabase jdbcDatabase,
                                            final Stream<PartialAirbyteMessage> records,
                                            final Supplier<UUID> uuidSupplier,
                                            final boolean sem)
      throws SQLException {
    final Iterator<PartialAirbyteMessage> iterator = records.iterator();
    if (!iterator.hasNext()) {
      return;
    }
    jdbcDatabase.execute(connection -> {
      // Strategy: We want to use PreparedStatement because it handles binding values to the SQL query
      // (e.g. handling formatting timestamps). A PreparedStatement statement is created by supplying the
      // full SQL string at creation time. Then subsequently specifying which values are bound to the
      // string. Thus there will be two loops below.
      // 1) Loop over records to build the full string and query parameters
      // 2) Loop over the params and bind the appropriate values to the PreparedStatement.
      // We also partition the query to run on 10k records at a time, since some DBs set a max limit on
      // how many records can be inserted at once
      // TODO(sherif) this should use a smarter, destination-aware partitioning scheme instead of 10k by
      // default
      while (iterator.hasNext()) {
        final StringBuilder sql = new StringBuilder(insertQueryComponent);
        final List<Object> params = new ArrayList<>();
        for (int i = 0; i < 10_000 && iterator.hasNext(); i++) {
          final PartialAirbyteMessage record = iterator.next();
          sql.append(recordQueryComponent);
          params.add(uuidSupplier.get().toString());
          params.add(record.getSerialized());
          params.add(Timestamp.from(Instant.ofEpochMilli(record.getRecord().getEmittedAt())));
        }

        final String s = sql.toString();
        final String s1 = s.substring(0, s.length() - 2) + (sem ? ";" : "");
        try (final PreparedStatement statement = connection.prepareStatement(s1)) {
          // second loop: bind values to the SQL string.
          for (int i = 0; i < params.size(); i++) {
            // Note that params are 1-indexed.
            statement.setObject(i + 1, params.get(i));
          }

          statement.execute();
        }
      }
    });
  }

}
