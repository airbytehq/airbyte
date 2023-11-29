/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.ResultSet;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.List;
import java.util.Optional;
import org.jooq.impl.DSL;

public class RedshiftDestinationHandler extends JdbcDestinationHandler {

  // Redshift doesn't seem to let you actually specify HH:MM TZ offsets, so we have
  // build our own formatter rather than just use Instant.parse
  private static final DateTimeFormatter TIMESTAMPTZ_FORMAT = new DateTimeFormatterBuilder()
      .append(DateTimeFormatter.ISO_LOCAL_DATE)
      .appendLiteral(' ')
      .append(DateTimeFormatter.ISO_LOCAL_TIME)
      .append(DateTimeFormatter.ofPattern("X"))
      .toFormatter();

  public RedshiftDestinationHandler(final String databaseName, final JdbcDatabase jdbcDatabase) {
    super(databaseName, jdbcDatabase);
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) throws Exception {
    // Redshift doesn't have an information_schema.tables table, so we have to use SVV_TABLE_INFO.
    // From https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_TABLE_INFO.html:
    // > The SVV_TABLE_INFO view doesn't return any information for empty tables.
    // So we just query for our specific table, and if we get no rows back,
    // then we assume the table is empty.
    // Note that because the column names are reserved words (table, schema, database),
    // we need to enquote them.
    final List<JsonNode> query = jdbcDatabase.queryJsons(
        """
        SELECT 1
        FROM SVV_TABLE_INFO
        WHERE "database" = ?
          AND "schema" = ?
          AND "table" = ?
        """,
        databaseName,
        id.finalNamespace(),
        id.finalName());
    return query.isEmpty();
  }

  @Override
  public Optional<Instant> getMinTimestampForSync(final StreamId id) throws Exception {
    final ResultSet tables = jdbcDatabase.getMetaData().getTables(
        databaseName,
        id.rawNamespace(),
        id.rawName(),
        null);
    if (!tables.next()) {
      return Optional.empty();
    }
    // Redshift timestamps have microsecond precision, but it's basically impossible to work with that.
    // Decrement by 1 second instead.
    // And use two explicit queries because docs don't specify whether COALESCE
    // short-circuits evaluation.
    // This first query tries to find the oldest raw record with loaded_at = NULL
    Optional<String> minUnloadedTimestamp = Optional.ofNullable(jdbcDatabase.queryStrings(
        conn -> conn.createStatement().executeQuery(
            DSL.select(DSL.field("MIN(_airbyte_extracted_at) - INTERVAL '1 second'").as("min_timestamp"))
                .from(DSL.name(id.rawNamespace(), id.rawName()))
                .where(DSL.condition("_airbyte_loaded_at IS NULL"))
                .getSQL()),
        // The query will always return exactly one record, so use .get(0)
        record -> record.getString("min_timestamp")).get(0));
    if (minUnloadedTimestamp.isEmpty()) {
      // If there are no unloaded raw records, then we can safely skip all existing raw records.
      // This second query just finds the newest raw record.
      minUnloadedTimestamp = Optional.ofNullable(jdbcDatabase.queryStrings(
          conn -> conn.createStatement().executeQuery(
              DSL.select(DSL.field("MAX(_airbyte_extracted_at)").as("min_timestamp"))
                  .from(DSL.name(id.rawNamespace(), id.rawName()))
                  .getSQL()),
          record -> record.getString("min_timestamp")).get(0));
    }
    return minUnloadedTimestamp.map(RedshiftDestinationHandler::parseInstant);
  }

  private static Instant parseInstant(final String ts) {
    return TIMESTAMPTZ_FORMAT.parse(ts, Instant::from);
  }

}
