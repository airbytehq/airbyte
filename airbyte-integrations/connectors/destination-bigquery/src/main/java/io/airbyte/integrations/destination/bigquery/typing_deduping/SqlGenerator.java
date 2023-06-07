package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;

public interface SqlGenerator<DialectTableDefinition, DialectType> {

  /**
   * In general, callers should not directly instantiate this class. Use {@link #quoteStreamId(String, String)} instead.
   */
  record QuotedStreamId(String namespace, String name) {

  }

  /**
   * In general, callers should not directly instantiate this class. Use {@link #quoteColumnId(String)} instead.
   */
  record QuotedColumnId(String name) {

  }

  QuotedStreamId quoteStreamId(String namespace, String name);

  QuotedColumnId quoteColumnId(String name);

  DialectType toDialectType(AirbyteType type);

  record StreamConfig<DialectType>(QuotedStreamId id,
                                   SyncMode syncMode,
                                   DestinationSyncMode destinationSyncMode,
                                   List<QuotedColumnId> primaryKey,
                                   Optional<QuotedColumnId> cursor,
                                   LinkedHashMap<String, DialectType> columns) {

  }

  default StreamConfig<DialectType> toStreamConfig(ConfiguredAirbyteStream stream) {
    AirbyteType schema = AirbyteType.fromJsonSchema(stream.getStream().getJsonSchema());
    final LinkedHashMap<String, AirbyteType> airbyteColumns;
    if (schema instanceof AirbyteType.Object o) {
      airbyteColumns = o.properties();
    } else if (schema instanceof AirbyteType.OneOf o) {
      airbyteColumns = o.asColumns();
    } else {
      throw new IllegalArgumentException("Top-level schema must be an object");
    }

    if (stream.getPrimaryKey().stream().anyMatch(key -> key.size() > 1)) {
      throw new IllegalArgumentException("Only top-level primary keys are supported");
    }
    final List<QuotedColumnId> primaryKey = stream.getPrimaryKey().stream().map(key -> quoteColumnId(key.get(0))).toList();

    if (stream.getCursorField().size() > 1) {
      throw new IllegalArgumentException("Only top-level cursors are supported");
    }
    final Optional<QuotedColumnId> cursor;
    if (stream.getCursorField().size() > 0) {
      cursor = Optional.of(quoteColumnId(stream.getCursorField().get(0)));
    } else {
      cursor = Optional.empty();
    }

    return new StreamConfig<>(
        quoteStreamId(stream.getStream().getNamespace(), stream.getStream().getName()),
        stream.getSyncMode(),
        stream.getDestinationSyncMode(),
        primaryKey,
        cursor,
        airbyteColumns.entrySet().stream().collect(
            LinkedHashMap::new,
            (map, entry) -> map.put(entry.getKey(), toDialectType(entry.getValue())),
            LinkedHashMap::putAll)
    );
  }

  /**
   * Generate a SQL statement to create a fresh table to match the given stream.
   * <p>
   * The generated SQL may throw an exception if the table already exists. Callers should use {@link #alterTable(StreamConfig, java.lang.Object)} if
   * the table is known to exist.
   */
  String createTable(final StreamConfig<DialectType> stream);

  /**
   * Generate a SQL statement to alter an existing table to match the given stream.
   * <p>
   * The operations may differ based on the existing table definition (BigQuery does not allow altering a partitioning scheme and requires you to
   * recreate+rename the table; snowflake only allows altering some column types to certain other types, etc.).
   */
  String alterTable(final StreamConfig<DialectType> stream, DialectTableDefinition existingTable);

  /**
   * Generate a SQL statement to copy new data from the raw table into the final table.
   */
  // TODO maybe this should be broken into smaller methods, idk
  String updateTable(final StreamConfig<DialectType> stream);

}
