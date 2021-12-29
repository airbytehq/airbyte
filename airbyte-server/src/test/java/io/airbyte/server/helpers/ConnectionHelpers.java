/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import io.airbyte.api.model.ConnectionSchedule.TimeUnitEnum;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ResourceRequirements;
import io.airbyte.api.model.SyncMode;
import io.airbyte.commons.text.Names;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.Schedule.TimeUnit;
import io.airbyte.config.StandardSync;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.workers.helper.CatalogConverter;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

public class ConnectionHelpers {

  private static final String STREAM_NAME = "users-data";
  private static final String FIELD_NAME = "id";
  private static final String BASIC_SCHEDULE_TIME_UNIT = "days";
  private static final long BASIC_SCHEDULE_UNITS = 1L;

  // only intended for unit tests, so intentionally set very high to ensure they aren't being used
  // elsewhere
  public static final io.airbyte.config.ResourceRequirements TESTING_RESOURCE_REQUIREMENTS = new io.airbyte.config.ResourceRequirements()
      .withCpuLimit("100g")
      .withCpuRequest("100g")
      .withMemoryLimit("100g")
      .withMemoryRequest("100g");

  public static StandardSync generateSyncWithSourceId(final UUID sourceId) {
    final UUID connectionId = UUID.randomUUID();

    return new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(generateBasicConfiguredAirbyteCatalog())
        .withSourceId(sourceId)
        .withDestinationId(UUID.randomUUID())
        .withOperationIds(List.of(UUID.randomUUID()))
        .withManual(false)
        .withSchedule(generateBasicSchedule())
        .withResourceRequirements(TESTING_RESOURCE_REQUIREMENTS);
  }

  public static StandardSync generateSyncWithDestinationId(final UUID destinationId) {
    final UUID connectionId = UUID.randomUUID();

    return new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(generateBasicConfiguredAirbyteCatalog())
        .withSourceId(UUID.randomUUID())
        .withDestinationId(destinationId)
        .withOperationIds(List.of(UUID.randomUUID()))
        .withManual(true);
  }

  public static ConnectionSchedule generateBasicConnectionSchedule() {
    return new ConnectionSchedule()
        .timeUnit(ConnectionSchedule.TimeUnitEnum.fromValue(BASIC_SCHEDULE_TIME_UNIT))
        .units(BASIC_SCHEDULE_UNITS);
  }

  public static Schedule generateBasicSchedule() {
    return new Schedule()
        .withTimeUnit(TimeUnit.fromValue(BASIC_SCHEDULE_TIME_UNIT))
        .withUnits(BASIC_SCHEDULE_UNITS);
  }

  public static ConnectionRead generateExpectedConnectionRead(final UUID connectionId,
                                                              final UUID sourceId,
                                                              final UUID destinationId,
                                                              final List<UUID> operationIds) {

    return new ConnectionRead()
        .connectionId(connectionId)
        .sourceId(sourceId)
        .destinationId(destinationId)
        .operationIds(operationIds)
        .name("presto to hudi")
        .namespaceDefinition(io.airbyte.api.model.NamespaceDefinitionType.SOURCE)
        .namespaceFormat(null)
        .prefix("presto_to_hudi")
        .status(ConnectionStatus.ACTIVE)
        .schedule(generateBasicConnectionSchedule())
        .syncCatalog(ConnectionHelpers.generateBasicApiCatalog())
        .resourceRequirements(new ResourceRequirements()
            .cpuRequest(TESTING_RESOURCE_REQUIREMENTS.getCpuRequest())
            .cpuLimit(TESTING_RESOURCE_REQUIREMENTS.getCpuLimit())
            .memoryRequest(TESTING_RESOURCE_REQUIREMENTS.getMemoryRequest())
            .memoryLimit(TESTING_RESOURCE_REQUIREMENTS.getMemoryLimit()));
  }

  public static ConnectionRead generateExpectedConnectionRead(final StandardSync standardSync) {
    final ConnectionRead connectionRead = generateExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceId(),
        standardSync.getDestinationId(),
        standardSync.getOperationIds());

    if (standardSync.getSchedule() == null) {
      connectionRead.schedule(null);
    } else {
      connectionRead.schedule(new ConnectionSchedule()
          .timeUnit(TimeUnitEnum.fromValue(standardSync.getSchedule().getTimeUnit().value()))
          .units(standardSync.getSchedule().getUnits()));
    }

    return connectionRead;
  }

  public static ConnectionRead connectionReadFromStandardSync(final StandardSync standardSync) {
    final ConnectionRead connectionRead = new ConnectionRead();
    connectionRead
        .connectionId(standardSync.getConnectionId())
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId())
        .operationIds(standardSync.getOperationIds())
        .name(standardSync.getName())
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix());

    if (standardSync.getNamespaceDefinition() != null) {
      connectionRead
          .namespaceDefinition(io.airbyte.api.model.NamespaceDefinitionType.fromValue(standardSync.getNamespaceDefinition().value()));
    }
    if (standardSync.getStatus() != null) {
      connectionRead.status(io.airbyte.api.model.ConnectionStatus.fromValue(standardSync.getStatus().value()));
    }
    if (standardSync.getSchedule() != null) {
      connectionRead.schedule(new io.airbyte.api.model.ConnectionSchedule()
          .timeUnit(TimeUnitEnum.fromValue(standardSync.getSchedule().getTimeUnit().value()))
          .units(standardSync.getSchedule().getUnits()));
    }
    if (standardSync.getCatalog() != null) {
      connectionRead.syncCatalog(CatalogConverter.toApi(standardSync.getCatalog()));
    }
    if (standardSync.getResourceRequirements() != null) {
      connectionRead.resourceRequirements(new io.airbyte.api.model.ResourceRequirements()
          .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
          .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
          .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit())
          .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest()));
    }
    return connectionRead;
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
