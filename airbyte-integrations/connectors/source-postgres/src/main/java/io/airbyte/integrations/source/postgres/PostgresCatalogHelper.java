/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_LSN;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class PostgresCatalogHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCatalogHelper.class);

  private PostgresCatalogHelper() {}

  /*
   * It isn't possible to recreate the state of the original database unless we include extra
   * information (like an oid) when using logical replication. By limiting to Full Refresh when we
   * don't have a primary key we dodge the problem for now. As a work around a CDC and non-CDC source
   * could be configured if there's a need to replicate a large non-PK table.
   *
   * Note: in place mutation.
   */
  public static AirbyteStream removeIncrementalWithoutPk(final AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      final List<SyncMode> syncModes = new ArrayList<>(stream.getSupportedSyncModes());
      syncModes.remove(SyncMode.INCREMENTAL);
      stream.setSupportedSyncModes(syncModes);
    }

    return stream;
  }

  /**
   * This method is used for CDC sync in order to overwrite sync modes for cursor fields cause cdc use
   * another cursor logic
   *
   * @param stream - airbyte stream
   * @return will return list of sync modes
   */
  public static AirbyteStream overrideSyncModes(final AirbyteStream stream) {
    return stream.withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
  }

  /*
   * Set all streams that do have incremental to sourceDefined, so that the user cannot set or
   * override a cursor field.
   *
   * Note: in place mutation.
   */
  public static AirbyteStream setIncrementalToSourceDefined(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setSourceDefinedCursor(true);
    }

    return stream;
  }

  // Note: in place mutation.
  public static AirbyteStream addCdcMetadataColumns(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    properties.set(DebeziumEventConverter.CDC_LSN, numberType);
    properties.set(DebeziumEventConverter.CDC_UPDATED_AT, stringType);
    properties.set(DebeziumEventConverter.CDC_DELETED_AT, stringType);

    return stream;
  }

  /**
   * Modifies streams that are NOT present in the publication to be full-refresh only streams. Users
   * should be able to replicate these streams, just not in incremental mode as they have no
   * associated publication. Previously, we also setSourceDefinedCursor(false) and
   * setSourceDefinedPrimaryKey(List.of()) for streams that are in the catalog but not in the CDC
   * publication, but now that full refresh streams can be resumable, we should include this
   * information.
   */
  public static AirbyteStream setFullRefreshForNonPublicationStreams(final AirbyteStream stream,
                                                                     final Set<AirbyteStreamNameNamespacePair> publicizedTablesInCdc) {
    if (!publicizedTablesInCdc.contains(new AirbyteStreamNameNamespacePair(stream.getName(), stream.getNamespace()))) {
      stream.setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    }
    return stream;
  }

  /**
   * @return tables included in the publication. When it is not CDC mode, returns an empty set.
   */
  public static Set<AirbyteStreamNameNamespacePair> getPublicizedTables(final JdbcDatabase database) throws SQLException {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (sourceConfig == null || !PostgresUtils.isCdc(sourceConfig)) {
      return Collections.emptySet();
    }

    final String publication = sourceConfig.get("replication_method").get("publication").asText();
    final List<JsonNode> tablesInPublication = database.queryJsons(
        "SELECT schemaname, tablename FROM pg_publication_tables WHERE pubname = ?", publication);
    final Set<AirbyteStreamNameNamespacePair> publicizedTables = tablesInPublication.stream()
        .map(table -> new AirbyteStreamNameNamespacePair(table.get("tablename").asText(), table.get("schemaname").asText()))
        .collect(Collectors.toSet());
    LOGGER.info("For CDC, only tables in publication {} will be included in the sync: {}", publication,
        publicizedTables.stream().map(pair -> pair.getNamespace() + "." + pair.getName()).toList());

    return publicizedTables;
  }

  /*
   * To prepare for Destination v2, cdc streams must have a default cursor field this defaults to lsn
   * as a cursor as it is monotonically increasing and unique
   */
  public static AirbyteStream setDefaultCursorFieldForCdc(final AirbyteStream stream) {
    stream.setDefaultCursorField(ImmutableList.of(CDC_LSN));
    return stream;
  }

}
