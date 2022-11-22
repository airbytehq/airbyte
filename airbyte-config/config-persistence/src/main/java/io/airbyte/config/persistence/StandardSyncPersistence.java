/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION_OPERATION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.STATE;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.select;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorType;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.StandardSync;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.configs.jooq.generated.tables.Actor;
import io.airbyte.db.instance.configs.jooq.generated.tables.ActorDefinition;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.SelectJoinStep;

public class StandardSyncPersistence {

  private record StandardSyncIdsWithProtocolVersions(
                                                     UUID standardSyncId,
                                                     UUID sourceDefId,
                                                     Version sourceProtocolVersion,
                                                     UUID destinationDefId,
                                                     Version destinationProtocolVersion) {}

  private final ExceptionWrappingDatabase database;

  public StandardSyncPersistence(final Database database) {
    this.database = new ExceptionWrappingDatabase(database);
  }

  public StandardSync getStandardSync(final UUID connectionId) throws IOException, ConfigNotFoundException {
    return getStandardSyncWithMetadata(connectionId).getConfig();
  }

  public ConfigWithMetadata<StandardSync> getStandardSyncWithMetadata(final UUID connectionId) throws IOException, ConfigNotFoundException {
    final List<ConfigWithMetadata<StandardSync>> result = listStandardSyncWithMetadata(Optional.of(connectionId));

    final boolean foundMoreThanOneConfig = result.size() > 1;
    if (result.isEmpty()) {
      throw new ConfigNotFoundException(ConfigSchema.STANDARD_SYNC, connectionId.toString());
    } else if (foundMoreThanOneConfig) {
      throw new IllegalStateException(String.format("Multiple %s configs found for ID %s: %s", ConfigSchema.STANDARD_SYNC, connectionId, result));
    }
    return result.get(0);
  }

  public List<StandardSync> listStandardSync() throws IOException {
    return listStandardSyncWithMetadata().stream().map(ConfigWithMetadata::getConfig).toList();
  }

  public List<ConfigWithMetadata<StandardSync>> listStandardSyncWithMetadata() throws IOException {
    return listStandardSyncWithMetadata(Optional.empty());
  }

  public void writeStandardSync(final StandardSync standardSync) throws IOException {
    database.transaction(ctx -> {
      writeStandardSync(standardSync, ctx);
      return null;
    });
  }

  public void deleteStandardSync(final UUID standardSyncId) throws IOException {
    database.transaction(ctx -> {
      PersistenceHelpers.deleteConfig(CONNECTION_OPERATION, CONNECTION_OPERATION.CONNECTION_ID, standardSyncId, ctx);
      PersistenceHelpers.deleteConfig(STATE, STATE.CONNECTION_ID, standardSyncId, ctx);
      PersistenceHelpers.deleteConfig(CONNECTION, CONNECTION.ID, standardSyncId, ctx);
      return null;
    });
  }

  /**
   * For the StandardSyncs related to actorDefinitionId, clear the unsupported protocol version flag
   * if both connectors are now within support range.
   *
   * @param actorDefinitionId the actorDefinitionId to query
   * @param actorType the ActorType of actorDefinitionId
   * @param supportedRange the supported range of protocol versions
   */
  public void clearUnsupportedProtocolVersionFlag(final UUID actorDefinitionId,
                                                  final ActorType actorType,
                                                  final AirbyteProtocolVersionRange supportedRange)
      throws IOException {
    final Stream<StandardSyncIdsWithProtocolVersions> candidateSyncs = database.query(ctx -> findDisabledSyncs(ctx, actorDefinitionId, actorType));
    final List<UUID> standardSyncsToReEnable = candidateSyncs
        .filter(sync -> supportedRange.isSupported(sync.sourceProtocolVersion()) && supportedRange.isSupported(sync.destinationProtocolVersion()))
        .map(StandardSyncIdsWithProtocolVersions::standardSyncId)
        .toList();
    database.query(ctx -> {
      clearProtocolVersionFlag(ctx, standardSyncsToReEnable);
      return null;
    });
  }

  private List<ConfigWithMetadata<StandardSync>> listStandardSyncWithMetadata(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(CONNECTION);
      if (configId.isPresent()) {
        return query.where(CONNECTION.ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });

    final List<ConfigWithMetadata<StandardSync>> standardSyncs = new ArrayList<>();
    for (final Record record : result) {
      final StandardSync standardSync = DbConverter.buildStandardSync(record, connectionOperationIds(record.get(CONNECTION.ID)));
      if (ScheduleHelpers.isScheduleTypeMismatch(standardSync)) {
        throw new RuntimeException("unexpected schedule type mismatch");
      }
      standardSyncs.add(new ConfigWithMetadata<>(
          record.get(CONNECTION.ID).toString(),
          ConfigSchema.STANDARD_SYNC.name(),
          record.get(CONNECTION.CREATED_AT).toInstant(),
          record.get(CONNECTION.UPDATED_AT).toInstant(),
          standardSync));
    }
    return standardSyncs;
  }

  private List<UUID> connectionOperationIds(final UUID connectionId) throws IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(CONNECTION_OPERATION)
        .where(CONNECTION_OPERATION.CONNECTION_ID.eq(connectionId))
        .fetch());

    final List<UUID> ids = new ArrayList<>();
    for (final Record record : result) {
      ids.add(record.get(CONNECTION_OPERATION.OPERATION_ID));
    }

    return ids;
  }

  private void writeStandardSync(final StandardSync standardSync, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    final boolean isExistingConfig = ctx.fetchExists(select()
        .from(CONNECTION)
        .where(CONNECTION.ID.eq(standardSync.getConnectionId())));

    if (ScheduleHelpers.isScheduleTypeMismatch(standardSync)) {
      throw new RuntimeException("unexpected schedule type mismatch");
    }

    if (isExistingConfig) {
      ctx.update(CONNECTION)
          .set(CONNECTION.ID, standardSync.getConnectionId())
          .set(CONNECTION.NAMESPACE_DEFINITION, Enums.toEnum(standardSync.getNamespaceDefinition().value(),
              io.airbyte.db.instance.configs.jooq.generated.enums.NamespaceDefinitionType.class).orElseThrow())
          .set(CONNECTION.NAMESPACE_FORMAT, standardSync.getNamespaceFormat())
          .set(CONNECTION.PREFIX, standardSync.getPrefix())
          .set(CONNECTION.SOURCE_ID, standardSync.getSourceId())
          .set(CONNECTION.DESTINATION_ID, standardSync.getDestinationId())
          .set(CONNECTION.NAME, standardSync.getName())
          .set(CONNECTION.CATALOG, JSONB.valueOf(Jsons.serialize(standardSync.getCatalog())))
          .set(CONNECTION.STATUS, standardSync.getStatus() == null ? null
              : Enums.toEnum(standardSync.getStatus().value(),
                  io.airbyte.db.instance.configs.jooq.generated.enums.StatusType.class).orElseThrow())
          .set(CONNECTION.SCHEDULE, JSONB.valueOf(Jsons.serialize(standardSync.getSchedule())))
          .set(CONNECTION.MANUAL, standardSync.getManual())
          .set(CONNECTION.SCHEDULE_TYPE,
              standardSync.getScheduleType() == null ? null
                  : Enums.toEnum(standardSync.getScheduleType().value(),
                      io.airbyte.db.instance.configs.jooq.generated.enums.ScheduleType.class)
                      .orElseThrow())
          .set(CONNECTION.SCHEDULE_DATA, JSONB.valueOf(Jsons.serialize(standardSync.getScheduleData())))
          .set(CONNECTION.RESOURCE_REQUIREMENTS,
              JSONB.valueOf(Jsons.serialize(standardSync.getResourceRequirements())))
          .set(CONNECTION.UPDATED_AT, timestamp)
          .set(CONNECTION.SOURCE_CATALOG_ID, standardSync.getSourceCatalogId())
          .set(CONNECTION.BREAKING_CHANGE, standardSync.getBreakingChange())
          .set(CONNECTION.GEOGRAPHY, Enums.toEnum(standardSync.getGeography().value(),
              io.airbyte.db.instance.configs.jooq.generated.enums.GeographyType.class).orElseThrow())
          .where(CONNECTION.ID.eq(standardSync.getConnectionId()))
          .execute();

      ctx.deleteFrom(CONNECTION_OPERATION)
          .where(CONNECTION_OPERATION.CONNECTION_ID.eq(standardSync.getConnectionId()))
          .execute();
      for (final UUID operationIdFromStandardSync : standardSync.getOperationIds()) {
        ctx.insertInto(CONNECTION_OPERATION)
            .set(CONNECTION_OPERATION.ID, UUID.randomUUID())
            .set(CONNECTION_OPERATION.CONNECTION_ID, standardSync.getConnectionId())
            .set(CONNECTION_OPERATION.OPERATION_ID, operationIdFromStandardSync)
            .set(CONNECTION_OPERATION.CREATED_AT, timestamp)
            .set(CONNECTION_OPERATION.UPDATED_AT, timestamp)
            .execute();
      }
    } else {
      ctx.insertInto(CONNECTION)
          .set(CONNECTION.ID, standardSync.getConnectionId())
          .set(CONNECTION.NAMESPACE_DEFINITION, Enums.toEnum(standardSync.getNamespaceDefinition().value(),
              io.airbyte.db.instance.configs.jooq.generated.enums.NamespaceDefinitionType.class).orElseThrow())
          .set(CONNECTION.NAMESPACE_FORMAT, standardSync.getNamespaceFormat())
          .set(CONNECTION.PREFIX, standardSync.getPrefix())
          .set(CONNECTION.SOURCE_ID, standardSync.getSourceId())
          .set(CONNECTION.DESTINATION_ID, standardSync.getDestinationId())
          .set(CONNECTION.NAME, standardSync.getName())
          .set(CONNECTION.CATALOG, JSONB.valueOf(Jsons.serialize(standardSync.getCatalog())))
          .set(CONNECTION.STATUS, standardSync.getStatus() == null ? null
              : Enums.toEnum(standardSync.getStatus().value(),
                  io.airbyte.db.instance.configs.jooq.generated.enums.StatusType.class).orElseThrow())
          .set(CONNECTION.SCHEDULE, JSONB.valueOf(Jsons.serialize(standardSync.getSchedule())))
          .set(CONNECTION.MANUAL, standardSync.getManual())
          .set(CONNECTION.SCHEDULE_TYPE,
              standardSync.getScheduleType() == null ? null
                  : Enums.toEnum(standardSync.getScheduleType().value(),
                      io.airbyte.db.instance.configs.jooq.generated.enums.ScheduleType.class)
                      .orElseThrow())
          .set(CONNECTION.SCHEDULE_DATA, JSONB.valueOf(Jsons.serialize(standardSync.getScheduleData())))
          .set(CONNECTION.RESOURCE_REQUIREMENTS,
              JSONB.valueOf(Jsons.serialize(standardSync.getResourceRequirements())))
          .set(CONNECTION.SOURCE_CATALOG_ID, standardSync.getSourceCatalogId())
          .set(CONNECTION.GEOGRAPHY, Enums.toEnum(standardSync.getGeography().value(),
              io.airbyte.db.instance.configs.jooq.generated.enums.GeographyType.class).orElseThrow())
          .set(CONNECTION.BREAKING_CHANGE, standardSync.getBreakingChange())
          .set(CONNECTION.CREATED_AT, timestamp)
          .set(CONNECTION.UPDATED_AT, timestamp)
          .execute();
      for (final UUID operationIdFromStandardSync : standardSync.getOperationIds()) {
        ctx.insertInto(CONNECTION_OPERATION)
            .set(CONNECTION_OPERATION.ID, UUID.randomUUID())
            .set(CONNECTION_OPERATION.CONNECTION_ID, standardSync.getConnectionId())
            .set(CONNECTION_OPERATION.OPERATION_ID, operationIdFromStandardSync)
            .set(CONNECTION_OPERATION.CREATED_AT, timestamp)
            .set(CONNECTION_OPERATION.UPDATED_AT, timestamp)
            .execute();
      }
    }
  }

  private Stream<StandardSyncIdsWithProtocolVersions> findDisabledSyncs(final DSLContext ctx, final UUID actorDefId, final ActorType actorType) {
    // Table aliasing to help have a readable join
    final Actor source = ACTOR.as("source");
    final Actor destination = ACTOR.as("destination");
    final ActorDefinition sourceDef = ACTOR_DEFINITION.as("sourceDef");
    final ActorDefinition destDef = ACTOR_DEFINITION.as("destDef");

    // Retrieve all the connections currently disabled due to a bad protocol version
    // where the actor definition is matching the one provided to this function
    final Stream<StandardSyncIdsWithProtocolVersions> results = ctx
        .select(CONNECTION.ID, sourceDef.ID, sourceDef.PROTOCOL_VERSION, destDef.ID, destDef.PROTOCOL_VERSION)
        .from(CONNECTION)
        .join(source).on(CONNECTION.SOURCE_ID.eq(source.ID))
        .join(sourceDef).on(source.ACTOR_DEFINITION_ID.eq(sourceDef.ID))
        .join(destination).on(CONNECTION.DESTINATION_ID.eq(destination.ID))
        .join(destDef).on(destination.ACTOR_DEFINITION_ID.eq(destDef.ID))
        .where(
            CONNECTION.UNSUPPORTED_PROTOCOL_VERSION.eq(true).and(
                (actorType == ActorType.DESTINATION ? destDef : sourceDef).ID.eq(actorDefId)))
        .fetchStream()
        .map(r -> new StandardSyncIdsWithProtocolVersions(
            r.get(CONNECTION.ID),
            r.get(sourceDef.ID),
            AirbyteProtocolVersion.getWithDefault(r.get(sourceDef.PROTOCOL_VERSION)),
            r.get(destDef.ID),
            AirbyteProtocolVersion.getWithDefault(r.get(destDef.PROTOCOL_VERSION))));
    return results;
  }

  private void clearProtocolVersionFlag(final DSLContext ctx, final List<UUID> standardSyncIds) {
    ctx.update(CONNECTION)
        .set(CONNECTION.UNSUPPORTED_PROTOCOL_VERSION, false)
        .set(CONNECTION.UPDATED_AT, OffsetDateTime.now())
        .where(CONNECTION.ID.in(standardSyncIds))
        .execute();
  }

}
