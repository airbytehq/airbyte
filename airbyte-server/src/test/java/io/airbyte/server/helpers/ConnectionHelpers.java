/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.AirbyteCatalog;
import io.airbyte.api.model.AirbyteStream;
import io.airbyte.api.model.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.AirbyteStreamConfiguration;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.SyncMode;
import io.airbyte.commons.text.Names;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

public class ConnectionHelpers {

  private static final String STREAM_NAME = "users-data";
  private static final String FIELD_NAME = "id";

  public static StandardSync generateSyncWithSourceId(UUID sourceId) {
    final UUID connectionId = UUID.randomUUID();

    return new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(generateBasicConfiguredAirbyteCatalog())
        .withSourceId(sourceId)
        .withDestinationId(UUID.randomUUID());
  }

  public static StandardSync generateSyncWithDestinationId(UUID destinationId) {
    final UUID connectionId = UUID.randomUUID();

    return new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(generateBasicConfiguredAirbyteCatalog())
        .withSourceId(UUID.randomUUID())
        .withDestinationId(destinationId);
  }

  public static ConnectionSchedule generateBasicSchedule() {
    return new ConnectionSchedule()
        .timeUnit(ConnectionSchedule.TimeUnitEnum.DAYS)
        .units(1L);
  }

  public static ConnectionRead generateExpectedConnectionRead(UUID connectionId,
                                                              UUID sourceId,
                                                              UUID destinationId) {

    return new ConnectionRead()
        .connectionId(connectionId)
        .sourceId(sourceId)
        .destinationId(destinationId)
        .name("presto to hudi")
        .prefix("presto_to_hudi")
        .status(ConnectionStatus.ACTIVE)
        .schedule(generateBasicSchedule())
        .syncCatalog(ConnectionHelpers.generateBasicApiCatalog());
  }

  public static ConnectionRead generateExpectedConnectionRead(StandardSync standardSync) {
    return generateExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceId(),
        standardSync.getDestinationId());
  }

  public static StandardSyncSchedule generateSchedule(UUID connectionId) {
    final Schedule schedule = new Schedule()
        .withTimeUnit(Schedule.TimeUnit.DAYS)
        .withUnits(1L);

    return new StandardSyncSchedule()
        .withConnectionId(connectionId)
        .withSchedule(schedule)
        .withManual(false);
  }

  public static JsonNode generateBasicJsonSchema() {
    return CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING));
  }

  public static ConfiguredAirbyteCatalog generateBasicConfiguredAirbyteCatalog() {
    final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream()
        .withStream(generateBasicAirbyteStream())
        .withCursorField(Lists.newArrayList(FIELD_NAME))
        .withSyncMode(io.airbyte.protocol.models.SyncMode.INCREMENTAL)
        .withDestinationSyncMode(DestinationSyncMode.APPEND);
    return new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(stream));
  }

  private static io.airbyte.protocol.models.AirbyteStream generateBasicAirbyteStream() {
    return CatalogHelpers.createAirbyteStream(STREAM_NAME, Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING))
        .withDefaultCursorField(Lists.newArrayList(FIELD_NAME))
        .withSourceDefinedCursor(false)
        .withSupportedSyncModes(List.of(io.airbyte.protocol.models.SyncMode.FULL_REFRESH, io.airbyte.protocol.models.SyncMode.INCREMENTAL));
  }

  public static AirbyteCatalog generateBasicApiCatalog() {
    return new AirbyteCatalog().streams(Lists.newArrayList(new AirbyteStreamAndConfiguration()
        .stream(generateBasicApiStream())
        .config(generateBasicApiStreamConfig())));
  }

  private static AirbyteStreamConfiguration generateBasicApiStreamConfig() {
    return new AirbyteStreamConfiguration()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(Lists.newArrayList(FIELD_NAME))
        .destinationSyncMode(io.airbyte.api.model.DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName(Names.toAlphanumericAndUnderscore(STREAM_NAME))
        .selected(true);
  }

  private static AirbyteStream generateBasicApiStream() {
    return new AirbyteStream()
        .name(STREAM_NAME)
        .jsonSchema(generateBasicJsonSchema())
        .defaultCursorField(Lists.newArrayList(FIELD_NAME))
        .sourceDefinedCursor(false)
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
  }

}
