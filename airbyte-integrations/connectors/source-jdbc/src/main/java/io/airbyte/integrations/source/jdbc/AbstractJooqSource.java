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

package io.airbyte.integrations.source.jdbc;

import static org.jooq.impl.DSL.currentSchema;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.jooq.Record;
import org.jooq.SQLDialect;
import org.jooq.Schema;
import org.jooq.Table;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJooqSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJooqSource.class);

  private static final JSONFormat DB_JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private final String driverClass;
  private final SQLDialect dialect;

  public AbstractJooqSource(final String driverClass, final SQLDialect dialect) {
    this.driverClass = driverClass;
    this.dialect = dialect;
  }

  public abstract JsonNode toJdbcConfig(JsonNode config);

  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a JsonSchema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final Database database = createDatabase(config)) {
      // attempt to get current schema. this is a cheap query to sanity check that we can connect to the
      // database. `currentSchema()` is a jooq method that will run the appropriate query based on which
      // database it is connected to.
      database.query(this::getCurrentDatabaseName);

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.debug("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Can't connect with provided configuration.");
    }
  }

  protected String getCurrentDatabaseName(DSLContext ctx) {
    return ctx.select(currentSchema()).fetch().get(0).getValue(0, String.class);
  }

  @Override
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    try (final Database database = createDatabase(config)) {
      return new AirbyteCatalog()
          .withStreams(getTables(database)
              .stream()
              .map(t -> CatalogHelpers.createAirbyteStream(t.getName(), t.getFields()))
              .collect(Collectors.toList()));
    }
  }

  protected List<String> getExcludedInternalSchemas() {
    return List.of();
  }

  protected List<TableInfo> getTables(final Database database) throws Exception {
    return discoverInternal(database).stream()
        .map(t -> {
          final List<Field> fields = Arrays.stream(t.fields())
              .map(f -> Field.of(f.getName(), jooqDataTypeToJsonSchemaType(f.getDataType())))
              .collect(Collectors.toList());

          return new TableInfo(String.format("%s.%s", t.getSchema().getName(), t.getName()), fields);
        })
        .collect(Collectors.toList());
  }

  private List<Table<?>> discoverInternal(final Database database) throws Exception {
    return database.query(context -> {
      final List<Schema> schemas = context.meta().getSchemas();
      return schemas.stream()
          .filter(schema -> !getExcludedInternalSchemas().contains(schema.getName()))
          .flatMap(schema -> context.meta(schema).getTables().stream())
          .collect(Collectors.toList());
    });
  }

  @Override
  public Stream<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
    final Instant now = Instant.now();

    final Database database = createDatabase(config);

    final Map<String, Table<?>> tableNameToTable = discoverInternal(database).stream()
        .collect(Collectors.toMap(t -> String.format("%s.%s", t.getSchema().getName(), t.getName()), Function.identity()));

    Stream<AirbyteMessage> resultStream = Stream.empty();

    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final String streamName = airbyteStream.getStream().getName();
      if (!tableNameToTable.containsKey(streamName)) {
        continue;
      }

      final Set<String> selectedFields = CatalogHelpers.getTopLevelFieldNames(airbyteStream);

      final Table<?> table = tableNameToTable.get(streamName);
      final List<org.jooq.Field<?>> selectedDatabaseFields = Arrays.stream(table.fields())
          .filter(field -> selectedFields.contains(field.getName()))
          .collect(Collectors.toList());

      if (selectedDatabaseFields.isEmpty()) {
        continue;
      }

      final Stream<AirbyteMessage> stream;
      if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
        final JdbcStateManager stateManager = new JdbcStateManager(state == null ? new JdbcState() : Jsons.object(state, JdbcState.class));
        final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
        final JsonSchemaPrimitive cursorType = IncrementalUtils.getCursorType(airbyteStream, cursorField);
        final Optional<String> initialCursorOptional = stateManager.getOriginalCursor(streamName);

        final Stream<AirbyteMessage> internalMessageStream;
        if (initialCursorOptional.isPresent()) {
          final org.jooq.Field<?> cursorJooqField = Arrays
              .stream(table.fields())
              .filter(f -> f.getName().equals(cursorField))
              .findFirst()
              .orElseThrow(
                  () -> new IllegalStateException(String.format("Could not find cursor field %s in table %s", cursorField, table.getName())));

          final Stream<Record> queryStream = executeIncrementalQuery(
              database,
              selectedDatabaseFields,
              table,
              cursorJooqField,
              initialCursorOptional.get());
          internalMessageStream = getMessageStream(queryStream, streamName, now.toEpochMilli());
        } else {
          internalMessageStream = getMessageStream(executeFullRefreshQuery(database, selectedDatabaseFields, table), streamName, now.toEpochMilli());
        }

        final StateDecoratingIterator stateDecoratingIterator = new StateDecoratingIterator(
            internalMessageStream,
            stateManager,
            streamName,
            cursorField,
            initialCursorOptional.orElse(null),
            cursorType);

        stream = MoreStreams.toStream(stateDecoratingIterator);
      } else {
        stream = getMessageStream(executeFullRefreshQuery(database, selectedDatabaseFields, table), streamName, now.toEpochMilli());
      }

      resultStream = Stream.concat(resultStream, stream);
    }

    return resultStream.onClose(() -> Exceptions.toRuntime(database::close));
  }

  private static Stream<Record> executeFullRefreshQuery(Database database, List<org.jooq.Field<?>> jooqFields, Table<?> table) throws SQLException {
    return database.query(ctx -> ctx.select(jooqFields)
        .from(table)
        .fetchStream());
  }

  private static <T> Stream<Record> executeIncrementalQuery(Database database,
                                                            List<org.jooq.Field<?>> fields,
                                                            Table<?> table,
                                                            org.jooq.Field<T> cursorField,
                                                            String cursor)
      throws SQLException {

    return database.query(ctx -> ctx.select(fields)
        .from(table)
        .where(cursorField.greaterThan(AbstractJooqSource.toField(cursorField.getDataType(), cursor)))
        .fetchStream());
  }

  private static Stream<AirbyteMessage> getMessageStream(Stream<Record> recordStream, String streamName, long time) {
    return recordStream.map(r -> new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withEmittedAt(time)
            .withData(Jsons.deserialize(r.formatJSON(DB_JSON_FORMAT)))));
  }

  private Database createDatabase(JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        driverClass,
        dialect);
  }

  protected static class TableInfo {

    private final String name;
    private final List<Field> fields;

    public TableInfo(String name, List<Field> fields) {
      this.name = name;
      this.fields = fields;
    }

    public String getName() {
      return name;
    }

    public List<Field> getFields() {
      return fields;
    }

  }

  /**
   * Mapping of jooq data types to airbyte data types. When in doubt, fall back on string.
   *
   * @param jooqDataType - data type that can be encountered in jooq
   * @return airbyte data type
   */
  private static JsonSchemaPrimitive jooqDataTypeToJsonSchemaType(DataType<?> jooqDataType) {
    if (jooqDataType.isArray()) {
      return JsonSchemaPrimitive.ARRAY;
    } else if (jooqDataType.isBinary()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isDate()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isDateTime()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isEnum()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isInterval()) {
      // todo (cgardens) - not entirely sure if we prefer this or int.
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isLob()) {
      return JsonSchemaPrimitive.STRING;
      // superset of isInteger
    } else if (jooqDataType.isNumeric()) {
      return JsonSchemaPrimitive.NUMBER;
    } else if (jooqDataType.isString()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isTemporal()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isTime()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isTimestamp()) {
      return JsonSchemaPrimitive.STRING;
    } else if (jooqDataType.isUDT()) {
      return JsonSchemaPrimitive.STRING;
    } else {
      return JsonSchemaPrimitive.STRING;
    }
  }

  private static <T> org.jooq.Field<T> toField(DataType<T> jooqDataType, String value) {
    if (jooqDataType.isNumeric()) {
      return DSL.field(value, jooqDataType);
    } else if (jooqDataType.isString() || jooqDataType.isTemporal()) {
      // todo (cgardens) - this is bad because only works for mysql, psql, and sqlite. these are also the
      // only dialects that jooq supports in the free version, so this should not actually be an issue. it
      // is still sketchy.
      return DSL.field("'" + value + "'", jooqDataType);
    } else {
      throw new IllegalStateException(String.format("Cannot use column of type %s", jooqDataType.toString()));
    }
  }

}
