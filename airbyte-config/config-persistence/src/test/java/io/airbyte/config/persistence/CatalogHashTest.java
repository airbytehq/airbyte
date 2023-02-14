/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.base.Charsets;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.server.handlers.helpers.CatalogConverter;
import io.airbyte.commons.text.Names;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * Series of tests to troubleshoot https://github.com/airbytehq/oncall/issues/1413.
 */
class CatalogHashTest {

  private static final String EXPECTED_HASH = "7b5bf7e0";

  @Test
  void testFullCatalogFlowSingle() throws JsonValidationException, IOException {
    final String catalog = MoreResources.readResource("catalog.json");
    final String catalogHash = computeHash(catalog);
    assertEquals(EXPECTED_HASH, catalogHash);
  }

  @Test
  void testFullCatalogFlowAll() throws IOException {
    final List<String> catalogs = Arrays.asList(MoreResources.readResource("catalogs.json").split("\n"));
    final Set<String> hashes = catalogs.stream().map(this::computeHash).collect(Collectors.toSet());
    assertEquals(1, hashes.size());
    assertEquals(EXPECTED_HASH, hashes.iterator().next());
  }

  @Test
  void testFullCatalogFlowAllMultiThreaded() throws IOException {
    final List<String> catalogs = Arrays.asList(MoreResources.readResource("catalogs.json").split("\n"));
    final Set<String> hashes = catalogs.parallelStream().map(this::computeHash).collect(Collectors.toSet());
    assertEquals(1, hashes.size());
    assertEquals(EXPECTED_HASH, hashes.iterator().next());
  }

  private String computeHash(final String catalog) {
    try {
      final HashFunction hashFunction = Hashing.murmur3_32_fixed();
      final io.airbyte.protocol.models.v0.AirbyteCatalog airbyteCatalog = Jsons.deserialize(catalog,
          io.airbyte.protocol.models.v0.AirbyteCatalog.class);
      final io.airbyte.protocol.models.v0.AirbyteMessage v0AirbyteMessage = new io.airbyte.protocol.models.v0.AirbyteMessage().withType(
          io.airbyte.protocol.models.v0.AirbyteMessage.Type.CATALOG).withCatalog(airbyteCatalog);
      final String v0AirbyteMessageAsJson = Jsons.serialize(v0AirbyteMessage);
      final AirbyteMessage airbyteMessage = Jsons.deserialize(v0AirbyteMessageAsJson, AirbyteMessage.class);
      final io.airbyte.api.client.model.generated.AirbyteCatalog clientAirbyteCatalog = toAirbyteCatalogClientApi(airbyteMessage.getCatalog());
      final String clientApiAirbyteCatalog = Jsons.serialize(clientAirbyteCatalog);
      final io.airbyte.api.model.generated.AirbyteCatalog serverAirbyteCatalog = Jsons.deserialize(clientApiAirbyteCatalog,
          io.airbyte.api.model.generated.AirbyteCatalog.class);
      final AirbyteCatalog apiAirbyteCatalog = CatalogConverter.toProtocol(serverAirbyteCatalog);
      final String protocolAirbyteCatalog = Jsons.serialize(apiAirbyteCatalog);
      return hashFunction.hashBytes(protocolAirbyteCatalog.getBytes(Charsets.UTF_8)).toString();
    } catch (final JsonValidationException e) {
      e.printStackTrace();
      return null;
    }
  }

  private static io.airbyte.api.client.model.generated.AirbyteCatalog toAirbyteCatalogClientApi(
      final io.airbyte.protocol.models.AirbyteCatalog catalog) {
    return new io.airbyte.api.client.model.generated.AirbyteCatalog()
        .streams(catalog.getStreams()
            .stream()
            .map(stream -> toAirbyteStreamClientApi(stream))
            .map(s -> new io.airbyte.api.client.model.generated.AirbyteStreamAndConfiguration()
                .stream(s)
                .config(generateDefaultConfiguration(s)))
            .collect(Collectors.toList()));
  }

  private static io.airbyte.api.client.model.generated.AirbyteStream toAirbyteStreamClientApi(
      final io.airbyte.protocol.models.AirbyteStream stream) {
    return new io.airbyte.api.client.model.generated.AirbyteStream()
        .name(stream.getName())
        .jsonSchema(stream.getJsonSchema())
        .supportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(),
            io.airbyte.api.client.model.generated.SyncMode.class))
        .sourceDefinedCursor(stream.getSourceDefinedCursor())
        .defaultCursorField(stream.getDefaultCursorField())
        .sourceDefinedPrimaryKey(stream.getSourceDefinedPrimaryKey())
        .namespace(stream.getNamespace());
  }

  private static io.airbyte.api.client.model.generated.AirbyteStreamConfiguration generateDefaultConfiguration(
      final io.airbyte.api.client.model.generated.AirbyteStream stream) {
    final io.airbyte.api.client.model.generated.AirbyteStreamConfiguration result =
        new io.airbyte.api.client.model.generated.AirbyteStreamConfiguration()
            .aliasName(Names.toAlphanumericAndUnderscore(stream.getName()))
            .cursorField(stream.getDefaultCursorField())
            .destinationSyncMode(io.airbyte.api.client.model.generated.DestinationSyncMode.APPEND)
            .primaryKey(stream.getSourceDefinedPrimaryKey())
            .selected(true);
    if (stream.getSupportedSyncModes().size() > 0) {
      result.setSyncMode(Enums.convertTo(stream.getSupportedSyncModes().get(0),
          io.airbyte.api.client.model.generated.SyncMode.class));
    } else {
      result.setSyncMode(io.airbyte.api.client.model.generated.SyncMode.INCREMENTAL);
    }
    return result;
  }
}

