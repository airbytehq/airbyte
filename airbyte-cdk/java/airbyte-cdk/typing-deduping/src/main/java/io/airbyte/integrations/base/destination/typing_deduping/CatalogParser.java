/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;
import java.util.Optional;
import org.apache.commons.codec.digest.DigestUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CatalogParser {

  private static final Logger LOGGER = LoggerFactory.getLogger(CatalogParser.class);

  private final SqlGenerator<?> sqlGenerator;
  private final String rawNamespace;

  public CatalogParser(final SqlGenerator<?> sqlGenerator) {
    this(sqlGenerator, DEFAULT_AIRBYTE_INTERNAL_NAMESPACE);
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
      final StreamConfig actualStreamConfig;
      // Use empty string quote because we don't really care
      if (streamConfigs.stream().anyMatch(s -> s.id().finalTableId("").equals(originalStreamConfig.id().finalTableId("")))
          || streamConfigs.stream().anyMatch(s -> s.id().rawTableId("").equals(originalStreamConfig.id().rawTableId("")))) {
        final String originalNamespace = stream.getStream().getNamespace();
        final String originalName = stream.getStream().getName();

        LOGGER.info("Detected table name collision for {}.{}", originalNamespace, originalName);

        // ... this logic is ported from legacy normalization, and maybe should change?
        // We're taking a hash of the quoted namespace and the unquoted stream name
        final String hash = DigestUtils.sha1Hex(originalStreamConfig.id().finalNamespace() + "&airbyte&" + originalName).substring(0, 3);
        final String newName = originalName + "_" + hash;
        actualStreamConfig = new StreamConfig(
            sqlGenerator.buildStreamId(originalNamespace, newName, rawNamespace),
            originalStreamConfig.syncMode(),
            originalStreamConfig.destinationSyncMode(),
            originalStreamConfig.primaryKey(),
            originalStreamConfig.cursor(),
            originalStreamConfig.columns());
      } else {
        actualStreamConfig = originalStreamConfig;
      }
      streamConfigs.add(actualStreamConfig);

      // Populate some interesting strings into the exception handler string deinterpolator
      AirbyteExceptionHandler.addStringForDeinterpolation(actualStreamConfig.id().rawNamespace());
      AirbyteExceptionHandler.addStringForDeinterpolation(actualStreamConfig.id().rawName());
      AirbyteExceptionHandler.addStringForDeinterpolation(actualStreamConfig.id().finalNamespace());
      AirbyteExceptionHandler.addStringForDeinterpolation(actualStreamConfig.id().finalName());
      AirbyteExceptionHandler.addStringForDeinterpolation(actualStreamConfig.id().originalNamespace());
      AirbyteExceptionHandler.addStringForDeinterpolation(actualStreamConfig.id().originalName());
      actualStreamConfig.columns().keySet().forEach(columnId -> {
        AirbyteExceptionHandler.addStringForDeinterpolation(columnId.name());
        AirbyteExceptionHandler.addStringForDeinterpolation(columnId.originalName());
      });
      // It's (unfortunately) possible for a cursor/PK to be declared that don't actually exist in the
      // schema.
      // Add their strings explicitly.
      actualStreamConfig.cursor().ifPresent(cursor -> {
        AirbyteExceptionHandler.addStringForDeinterpolation(cursor.name());
        AirbyteExceptionHandler.addStringForDeinterpolation(cursor.originalName());
      });
      actualStreamConfig.primaryKey().forEach(pk -> {
        AirbyteExceptionHandler.addStringForDeinterpolation(pk.name());
        AirbyteExceptionHandler.addStringForDeinterpolation(pk.originalName());
      });
    }
    return new ParsedCatalog(streamConfigs);
  }

  // TODO maybe we should extract the column collision stuff to a separate method, since that's the
  // interesting bit
  @VisibleForTesting
  public StreamConfig toStreamConfig(final ConfiguredAirbyteStream stream) {
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
        LOGGER.info(
            "Detected column name collision for {}.{}.{}",
            stream.getStream().getNamespace(),
            stream.getStream().getName(),
            entry.getKey());
        // One of the existing columns has the same name. We need to handle this collision.
        // Append _1, _2, _3, ... to the column name until we find one that doesn't collide.
        int i = 1;
        while (true) {
          columnId = sqlGenerator.buildColumnId(entry.getKey(), "_" + i);
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
