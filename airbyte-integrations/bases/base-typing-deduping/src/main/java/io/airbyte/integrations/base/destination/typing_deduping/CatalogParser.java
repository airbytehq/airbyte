/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;
import java.util.Optional;
import org.apache.commons.codec.digest.DigestUtils;

public class CatalogParser {

  public static final String DEFAULT_RAW_TABLE_NAMESPACE = "airbyte_internal";
  private final SqlGenerator<?> sqlGenerator;
  private final String rawNamespace;

  public CatalogParser(final SqlGenerator<?> sqlGenerator) {
    this(sqlGenerator, DEFAULT_RAW_TABLE_NAMESPACE);
  }

  public CatalogParser(final SqlGenerator<?> sqlGenerator, final String rawNamespace) {
    this.sqlGenerator = sqlGenerator;
    this.rawNamespace = rawNamespace;
  }

  public ParsedCatalog parseCatalog(final ConfiguredAirbyteCatalog catalog) {
    // this code is bad and I feel bad
    // it's mostly a port of the old normalization logic to prevent tablename collisions.
    // tbh I have no idea if it works correctly.
    final List<StreamConfig> streamConfigs = new ArrayList<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final StreamConfig originalStreamConfig = toStreamConfig(stream);
      // Use empty string quote because we don't really care
      if (streamConfigs.stream().anyMatch(s -> s.id().finalTableId("").equals(originalStreamConfig.id().finalTableId("")))
          || streamConfigs.stream().anyMatch(s -> s.id().rawTableId("").equals(originalStreamConfig.id().rawTableId("")))) {
        final String originalNamespace = stream.getStream().getNamespace();
        final String originalName = stream.getStream().getName();
        // ... this logic is ported from legacy normalization, and maybe should change?
        // We're taking a hash of the quoted namespace and the unquoted stream name
        final String hash = DigestUtils.sha1Hex(originalStreamConfig.id().finalNamespace() + "&airbyte&" + originalName).substring(0, 3);
        final String newName = originalName + "_" + hash;
        streamConfigs.add(new StreamConfig(
            sqlGenerator.buildStreamId(originalNamespace, newName, rawNamespace),
            originalStreamConfig.syncMode(),
            originalStreamConfig.destinationSyncMode(),
            originalStreamConfig.primaryKey(),
            originalStreamConfig.cursor(),
            originalStreamConfig.columns()));
      } else {
        streamConfigs.add(originalStreamConfig);
      }
    }
    return new ParsedCatalog(streamConfigs);
  }

  private StreamConfig toStreamConfig(final ConfiguredAirbyteStream stream) {
    final AirbyteType schema = AirbyteType.fromJsonSchema(stream.getStream().getJsonSchema());
    final LinkedHashMap<String, AirbyteType> airbyteColumns;
    if (schema instanceof final Struct o) {
      airbyteColumns = o.properties();
    } else if (schema instanceof final Union u) {
      airbyteColumns = u.asColumns();
    } else {
      throw new IllegalArgumentException("Top-level schema must be an object");
    }

    if (stream.getPrimaryKey().stream().anyMatch(key -> key.size() > 1)) {
      throw new IllegalArgumentException("Only top-level primary keys are supported");
    }
    final List<ColumnId> primaryKey = stream.getPrimaryKey().stream().map(key -> sqlGenerator.buildColumnId(key.get(0))).toList();

    if (stream.getCursorField().size() > 1) {
      throw new IllegalArgumentException("Only top-level cursors are supported");
    }
    final Optional<ColumnId> cursor;
    if (stream.getCursorField().size() > 0) {
      cursor = Optional.of(sqlGenerator.buildColumnId(stream.getCursorField().get(0)));
    } else {
      cursor = Optional.empty();
    }

    // this code is really bad and I'm not convinced we need to preserve this behavior.
    // as with the tablename collisions thing above - we're trying to preserve legacy normalization's
    // naming conventions here.
    final LinkedHashMap<ColumnId, AirbyteType> columns = new LinkedHashMap<>();
    for (final Entry<String, AirbyteType> entry : airbyteColumns.entrySet()) {
      final ColumnId originalColumnId = sqlGenerator.buildColumnId(entry.getKey());
      ColumnId columnId;
      if (columns.keySet().stream().noneMatch(c -> c.canonicalName().equals(originalColumnId.canonicalName()))) {
        // None of the existing columns have the same name. We can add this new column as-is.
        columnId = originalColumnId;
      } else {
        // One of the existing columns has the same name. We need to handle this collision.
        // Append _1, _2, _3, ... to the column name until we find one that doesn't collide.
        int i = 1;
        while (true) {
          columnId = sqlGenerator.buildColumnId(entry.getKey() + "_" + i);
          final String canonicalName = columnId.canonicalName();
          if (columns.keySet().stream().noneMatch(c -> c.canonicalName().equals(canonicalName))) {
            break;
          } else {
            i++;
          }
        }
        // But we need to keep the original name so that we can still fetch it out of the JSON records.
        columnId = new ColumnId(
            columnId.name(),
            originalColumnId.originalName(),
            columnId.canonicalName());
      }

      columns.put(columnId, entry.getValue());
    }

    return new StreamConfig(
        sqlGenerator.buildStreamId(stream.getStream().getNamespace(), stream.getStream().getName(), rawNamespace),
        stream.getSyncMode(),
        stream.getDestinationSyncMode(),
        primaryKey,
        cursor,
        columns);
  }

}
