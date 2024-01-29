package io.airbyte.integrations.destination.mysql.typing_deduping;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.name;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.commons.exceptions.SQLRuntimeException;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MysqlDestinationHandler extends JdbcDestinationHandler {
  private static final Logger LOGGER = LoggerFactory.getLogger(MysqlDestinationHandler.class);

  public MysqlDestinationHandler(final String databaseName, final JdbcDatabase jdbcDatabase) {
    super(databaseName, jdbcDatabase, SQLDialect.MYSQL);
  }

  // mysql's ResultSet#getTimestamp() throws errors like
  // `java.sql.SQLDataException: Cannot convert string '2023-01-01T00:00:00Z' to java.sql.Timestamp value`
  // so we override the method and replace all of those calls with Instant.parse(rs.getString())
  // yes, this is dumb.
  @Override
  public InitialRawTableState getInitialRawTableState(final StreamId id) throws Exception {
    final boolean tableExists = jdbcDatabase.executeMetadataQuery(dbmetadata -> {
      LOGGER.info("Retrieving table from Db metadata: {} {} {}", databaseName, id.rawNamespace(), id.rawName());
      try (final ResultSet table = dbmetadata.getTables(databaseName, id.rawNamespace(), id.rawName(), null)) {
        return table.next();
      } catch (final SQLException e) {
        LOGGER.error("Failed to retrieve table info from metadata", e);
        throw new SQLRuntimeException(e);
      }
    });
    if (!tableExists) {
      // There's no raw table at all. Therefore there are no unprocessed raw records, and this sync
      // should not filter raw records by timestamp.
      return new InitialRawTableState(false, Optional.empty());
    }
    // And use two explicit queries because COALESCE might not short-circuit evaluation.
    // This first query tries to find the oldest raw record with loaded_at = NULL.
    // Unsafe query requires us to explicitly close the Stream, which is inconvenient,
    // but it's also the only method in the JdbcDatabase interface to return non-string/int types
    try (final Stream<Instant> timestampStream = jdbcDatabase.unsafeQuery(
        conn -> conn.prepareStatement(
            getDslContext().select(field("MIN(_airbyte_extracted_at)").as("min_timestamp"))
                .from(name(id.rawNamespace(), id.rawName()))
                .where(DSL.condition("_airbyte_loaded_at IS NULL"))
                .getSQL()),
        record -> parseInstant(record.getString("min_timestamp")))) {
      // Filter for nonNull values in case the query returned NULL (i.e. no unloaded records).
      final Optional<Instant> minUnloadedTimestamp = timestampStream.filter(Objects::nonNull).findFirst();
      if (minUnloadedTimestamp.isPresent()) {
        // Decrement by 1 second since timestamp precision varies between databases.
        final Optional<Instant> ts = minUnloadedTimestamp
            .map(i -> i.minus(1, ChronoUnit.SECONDS));
        return new InitialRawTableState(true, ts);
      }
    }
    // If there are no unloaded raw records, then we can safely skip all existing raw records.
    // This second query just finds the newest raw record.
    try (final Stream<Instant> timestampStream = jdbcDatabase.unsafeQuery(
        conn -> conn.prepareStatement(
            getDslContext().select(field("MAX(_airbyte_extracted_at)").as("min_timestamp"))
                .from(name(id.rawNamespace(), id.rawName()))
                .getSQL()),
        record -> parseInstant(record.getString("min_timestamp")))) {
      // Filter for nonNull values in case the query returned NULL (i.e. no raw records at all).
      final Optional<Instant> minUnloadedTimestamp = timestampStream.filter(Objects::nonNull).findFirst();
      return new InitialRawTableState(false, minUnloadedTimestamp);
    }
  }

  private static Instant parseInstant(final String ts) {
    // Instant.parse requires nonnull input.
    if (ts == null) {
      return null;
    }
    return Instant.parse(ts);
  }
}
