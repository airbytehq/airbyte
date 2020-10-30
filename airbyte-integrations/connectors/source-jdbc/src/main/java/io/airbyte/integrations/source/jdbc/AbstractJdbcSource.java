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
import io.airbyte.db.DatabaseHelper;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.io.IOException;
import java.sql.Connection;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.dbcp2.BasicDataSource;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.jooq.Named;
import org.jooq.SQLDialect;
import org.jooq.Schema;
import org.jooq.Table;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcSource.class);
  private static final JSONFormat DB_JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);
  private final String driverClass;
  private final SQLDialect dialect;

  public AbstractJdbcSource(String driverClass, SQLDialect dialect) {
    this.driverClass = driverClass;
    this.dialect = dialect;
  }

  public abstract JsonNode toJdbcConfig(JsonNode mySqlConfig);

  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a jsonschema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      final BasicDataSource connectionPool = getConnectionPool(config);
      // attempt to get current schema. this is a cheap query to sanity check that we can connect to the
      // database. `currentSchema()` is a jooq method that will run the appropriate query based on which
      // database it is connected to.
      DatabaseHelper.query(connectionPool, ctx -> ctx.select(currentSchema()).fetch(), dialect);

      connectionPool.close();
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    return new AirbyteCatalog()
        .withStreams(discoverInternal(config)
            .stream()
            .map(t -> {
              final List<Field> fields = Arrays.stream(t.fields()).map(f -> Field.of(f.getName(), jooqDataTypeToJsonSchemaType(f.getDataType())))
                  .collect(Collectors.toList());
              return CatalogHelpers.createAirbyteStream(t.getName(), fields);
            }).collect(Collectors.toList()));
  }

  private List<Table<?>> discoverInternal(JsonNode config) throws Exception {
    final BasicDataSource connectionPool = getConnectionPool(config);
    return DatabaseHelper.query(connectionPool, context -> {
      final String databaseName = context.select(currentSchema()).fetch().get(0).getValue(0, String.class);
      final List<Schema> databases = context.meta().getSchemas(databaseName);
      if (databases.size() > 1) {
        throw new IllegalStateException("found multiple databases with the same name.");
      }
      final Schema database = databases.get(0);
      return context.meta(database).getTables();
    }, dialect);
  }

  @Override
  public Stream<AirbyteMessage> read(JsonNode config, AirbyteCatalog catalog, JsonNode state) throws Exception {

    final Instant now = Instant.now();

    final BasicDataSource connectionPool = getConnectionPool(config);
    // We do not use the typical database wrappers here, because we do not want to close this
    // transaction until the stream is fully consumed by the calling process. We set connect.close() in
    // the close of the stream.
    final Connection connection = connectionPool.getConnection();
    final List<Table<?>> tables = discoverInternal(config);
    final DSLContext context = DatabaseHelper.getContext(connection, dialect);

    final Map<String, Table<?>> tableNameToTable = tables.stream().collect(Collectors.toMap(Named::getName, t -> t));
    return catalog.getStreams().stream()
        // iterate over streams in catalog and find corresponding table in the jooq schema.
        .map(airbyteStream -> ImmutablePair.of(airbyteStream, Optional.ofNullable(tableNameToTable.get(airbyteStream.getName()))))
        // filter out those that are not present in the jooq schema
        .filter(pair -> pair.getRight().isPresent())
        // for each stream pull the data
        .flatMap(pair -> {
          final AirbyteStream airbyteStream = pair.getLeft();
          final Table<?> table = pair.getRight().get();
          // extract column names from airbyte catalog. assumes table / column structure in the schema.
          // everything else gets flattened.
          final Set<String> fieldNames = CatalogHelpers.getTopLevelFieldNames(airbyteStream.getJsonSchema());
          // find columns in the jooq schema.
          final List<org.jooq.Field<?>> selectedFields = Arrays
              .stream(table.fields())
              .filter(field -> fieldNames.contains(field.getName()))
              .collect(Collectors.toList());

          if (selectedFields.isEmpty()) {
            return Stream.empty();
          }

          // return results as a stream that is mapped to an airbyte message.
          return context.select(selectedFields)
              .from(table)
              .fetch()
              .stream()
              .map(r -> new AirbyteMessage()
                  .withType(Type.RECORD)
                  .withRecord(new AirbyteRecordMessage()
                      .withStream(airbyteStream.getName())
                      .withEmittedAt(now.toEpochMilli())
                      .withData(Jsons.deserialize(r.formatJSON(DB_JSON_FORMAT)))));

        }).onClose(() -> Exceptions.toRuntime(connection::close));
  }

  private BasicDataSource getConnectionPool(JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);
    return DatabaseHelper.getConnectionPool(
        jdbcConfig.get("username").asText(),
        jdbcConfig.get("password").asText(),
        jdbcConfig.get("jdbc_url").asText(),
        driverClass);
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

}
