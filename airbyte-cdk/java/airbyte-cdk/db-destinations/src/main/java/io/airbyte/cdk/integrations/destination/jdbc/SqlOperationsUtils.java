/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Iterables;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

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
                                                   final List<AirbyteRecordMessage> records)
      throws SQLException {
    insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, jdbcDatabase, records, UUID::randomUUID, true);
  }

  @VisibleForTesting
  static void insertRawRecordsInSingleQuery(final String insertQueryComponent,
                                            final String recordQueryComponent,
                                            final JdbcDatabase jdbcDatabase,
                                            final List<AirbyteRecordMessage> records,
                                            final Supplier<UUID> uuidSupplier,
                                            final boolean sem)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }

    jdbcDatabase.execute(connection -> {

      // Strategy: We want to use PreparedStatement because it handles binding values to the SQL query
      // (e.g. handling formatting timestamps). A PreparedStatement statement is created by supplying the
      // full SQL string at creation time. Then subsequently specifying which values are bound to the
      // string. Thus there will be two loops below.
      // 1) Loop over records to build the full string.
      // 2) Loop over the records and bind the appropriate values to the string.
      // We also partition the query to run on 10k records at a time, since some DBs set a max limit on
      // how many records can be inserted at once
      // TODO(sherif) this should use a smarter, destination-aware partitioning scheme instead of 10k by
      // default
      for (final List<AirbyteRecordMessage> partition : Iterables.partition(records, 10_000)) {
        final StringBuilder sql = new StringBuilder(insertQueryComponent);
        partition.forEach(r -> sql.append(recordQueryComponent));
        final String s = sql.toString();
        final String s1 = s.substring(0, s.length() - 2) + (sem ? ";" : "");

        try (final PreparedStatement statement = connection.prepareStatement(s1)) {
          // second loop: bind values to the SQL string.
          // 1-indexed
          int i = 1;
          for (final AirbyteRecordMessage message : partition) {
            // Airbyte Raw ID
            statement.setString(i, uuidSupplier.get().toString());
            // Message Data
            statement.setString(i++, Jsons.serialize(message.getData()));
            // Extracted At
            statement.setTimestamp(i++, Timestamp.from(Instant.ofEpochMilli(message.getEmittedAt())));
            if (TypingAndDedupingFlag.isDestinationV2()) {
              // Loaded At
              statement.setTimestamp(i++, null);
            }
            i++;
          }

          statement.execute();
        }
      }
    });
  }

}
