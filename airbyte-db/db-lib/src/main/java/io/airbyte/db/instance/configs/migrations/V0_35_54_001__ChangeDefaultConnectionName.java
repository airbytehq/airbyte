/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.table;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_54_001__ChangeDefaultConnectionName extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_54_001__ChangeDefaultConnectionName.class);
  private static final String NAME = "name";

  public static void defaultConnectionName(final DSLContext ctx) {
    LOGGER.info("Updating connection name column");
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field(NAME, SQLDataType.VARCHAR(256).nullable(false));
    final List<Connection> connections = getConnections(ctx);

    for (final Connection connection : connections) {
      final Actor sourceActor = getActor(connection.getSourceId(), ctx);
      final Actor destinationActor = getActor(connection.getDestinationId(), ctx);
      final String connectionName = sourceActor.getName() + " <> " + destinationActor.getName();

      ctx.update(DSL.table("connection"))
          .set(name, connectionName)
          .where(id.eq(connection.getConnectionId()))
          .execute();
    }
  }

  static <T> List<Connection> getConnections(final DSLContext ctx) {
    LOGGER.info("Get connections having name default");
    final Field<String> name = DSL.field(NAME, SQLDataType.VARCHAR(36).nullable(false));
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> sourceId = DSL.field("source_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> destinationId = DSL.field("destination_id", SQLDataType.UUID.nullable(false));

    final Field<String> connectionName = DSL.field(NAME, SQLDataType.VARCHAR(256).nullable(false));
    final Result<Record> results = ctx.select(asterisk()).from(table("connection")).where(connectionName.eq("default")).fetch();

    return results.stream().map(record -> new Connection(
        record.get(name),
        record.get(id),
        record.get(sourceId),
        record.get(destinationId)))
        .collect(Collectors.toList());
  }

  static <T> Actor getActor(final UUID actorDefinitionId, final DSLContext ctx) {
    final Field<String> name = DSL.field(NAME, SQLDataType.VARCHAR(36).nullable(false));
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));

    final Result<Record> results = ctx.select(asterisk()).from(table("actor")).where(id.eq(actorDefinitionId)).fetch();

    return results.stream()
        .map(record -> new Actor(record.get(name))).toList().get(0);
  }

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    defaultConnectionName(ctx);
  }

  public static class Actor {

    private final String name;

    public <T> Actor(final String name) {
      this.name = name;
    }

    public String getName() {
      return this.name;
    }

  }

  public static class Connection {

    private final String name;
    private final UUID connectionId;
    private final UUID sourceId;
    private final UUID destinationId;

    public <T> Connection(final String name, final UUID id, final UUID sourceId, final UUID destinationId) {
      this.name = name;
      this.connectionId = id;
      this.sourceId = sourceId;
      this.destinationId = destinationId;
    }

    public String getName() {
      return this.name;
    }

    public UUID getSourceId() {
      return this.sourceId;
    }

    public UUID getDestinationId() {
      return this.destinationId;
    }

    public UUID getConnectionId() {
      return this.connectionId;
    }

  }

}
