package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedColumnId;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedStreamId;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;

public class CatalogParser<DialectType> {

  private final SqlGenerator<?, DialectType> sqlGenerator;

  public CatalogParser(final SqlGenerator<?, DialectType> sqlGenerator) {
    this.sqlGenerator = sqlGenerator;
  }

  record ParsedCatalog<DialectType>(List<StreamConfig<DialectType>> streams) {

  }

  public record StreamConfig<DialectType>(QuotedStreamId id,
                                          SyncMode syncMode,
                                          DestinationSyncMode destinationSyncMode,
                                          List<QuotedColumnId> primaryKey,
                                          Optional<QuotedColumnId> cursor,
                                          LinkedHashMap<QuotedColumnId, DialectType> columns) {

  }

  public ParsedCatalog<DialectType> parseCatalog(ConfiguredAirbyteCatalog catalog) {
    // TODO handle tablename collisions. final + raw
    return new ParsedCatalog<>(catalog.getStreams().stream().map(this::toStreamConfig).toList());
  }

  private StreamConfig<DialectType> toStreamConfig(ConfiguredAirbyteStream stream) {
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
    final List<QuotedColumnId> primaryKey = stream.getPrimaryKey().stream().map(key -> sqlGenerator.quoteColumnId(key.get(0))).toList();

    if (stream.getCursorField().size() > 1) {
      throw new IllegalArgumentException("Only top-level cursors are supported");
    }
    final Optional<QuotedColumnId> cursor;
    if (stream.getCursorField().size() > 0) {
      cursor = Optional.of(sqlGenerator.quoteColumnId(stream.getCursorField().get(0)));
    } else {
      cursor = Optional.empty();
    }

    return new StreamConfig<>(
        sqlGenerator.quoteStreamId(stream.getStream().getNamespace(), stream.getStream().getName()),
        stream.getSyncMode(),
        stream.getDestinationSyncMode(),
        primaryKey,
        cursor,
        airbyteColumns.entrySet().stream().collect(
            LinkedHashMap::new,
            // TODO handle column name collisions
            (map, entry) -> map.put(sqlGenerator.quoteColumnId(entry.getKey()), sqlGenerator.toDialectType(entry.getValue())),
            LinkedHashMap::putAll)
    );
  }
}
