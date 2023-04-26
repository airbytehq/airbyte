/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static com.mongodb.client.model.Filters.gt;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoException;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.AbstractDbSource;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.StringUtils;
import org.bson.BsonType;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbSource extends AbstractDbSource<BsonType, MongoDatabase> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbSource.class);

  public static void main(final String[] args) throws Exception {
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final var credentials = config.has(MongoUtils.USER) && config.has(JdbcUtils.PASSWORD_KEY)
        ? String.format("%s:%s@", config.get(MongoUtils.USER).asText(), config.get(JdbcUtils.PASSWORD_KEY).asText())
        : StringUtils.EMPTY;

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("connectionString", buildConnectionString(config, credentials))
        .put(JdbcUtils.DATABASE_KEY, config.get(JdbcUtils.DATABASE_KEY).asText())
        .build());
  }

  @Override
  protected MongoDatabase createDatabase(final JsonNode sourceConfig) throws Exception {
    final var dbConfig = toDatabaseConfig(sourceConfig);
    final MongoDatabase database = new MongoDatabase(dbConfig.get("connectionString").asText(),
        dbConfig.get(JdbcUtils.DATABASE_KEY).asText());
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(toDatabaseConfig(sourceConfig));
    return database;
  }

  @Override
  public List<CheckedConsumer<MongoDatabase, Exception>> getCheckOperations(final JsonNode config) {
    final List<CheckedConsumer<MongoDatabase, Exception>> checkList = new ArrayList<>();
    checkList.add(database -> {
      if (getAuthorizedCollections(database).isEmpty()) {
        throw new ConnectionErrorException("Unable to execute any operation on the source!");
      } else {
        LOGGER.info("The source passed the basic operation test!");
      }
    });
    return checkList;
  }

  @Override
  protected JsonSchemaType getAirbyteType(final BsonType fieldType) {
    return MongoUtils.getType(fieldType);
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.emptySet();
  }

  @Override
  protected List<TableInfo<CommonField<BsonType>>> discoverInternal(final MongoDatabase database)
      throws Exception {
    final List<TableInfo<CommonField<BsonType>>> tableInfos = new ArrayList<>();

    final Set<String> authorizedCollections = getAuthorizedCollections(database);
    authorizedCollections.parallelStream().forEach(collectionName -> {
      final MongoCollection<Document> collection = database.getCollection(collectionName);
      final List<CommonField<BsonType>> fields = MongoUtils.getUniqueFields(collection).stream().map(MongoUtils::nodeToCommonField).toList();

      // The field name _id is reserved for use as a primary key;
      final TableInfo<CommonField<BsonType>> tableInfo = TableInfo.<CommonField<BsonType>>builder()
          .nameSpace(database.getName())
          .name(collectionName)
          .fields(fields)
          .primaryKeys(List.of(MongoUtils.PRIMARY_KEY))
          .build();

      tableInfos.add(tableInfo);
    });
    return tableInfos;
  }

  private Set<String> getAuthorizedCollections(final MongoDatabase database) {
    /*
     * db.runCommand ({listCollections: 1.0, authorizedCollections: true, nameOnly: true }) the command
     * returns only those collections for which the user has privileges. For example, if a user has find
     * action on specific collections, the command returns only those collections; or, if a user has
     * find or any other action, on the database resource, the command lists all collections in the
     * database.
     */
    try {
      final Document document = database.getDatabase().runCommand(new Document("listCollections", 1)
          .append("authorizedCollections", true)
          .append("nameOnly", true))
          .append("filter", "{ 'type': 'collection' }");
      return document.toBsonDocument()
          .get("cursor").asDocument()
          .getArray("firstBatch")
          .stream()
          .map(bsonValue -> bsonValue.asDocument().getString("name").getValue())
          .collect(Collectors.toSet());

    } catch (final MongoSecurityException e) {
      final MongoCommandException exception = (MongoCommandException) e.getCause();
      throw new ConnectionErrorException(String.valueOf(exception.getCode()), e);
    } catch (final MongoException e) {
      throw new ConnectionErrorException(String.valueOf(e.getCode()), e);
    }
  }

  @Override
  protected List<TableInfo<CommonField<BsonType>>> discoverInternal(final MongoDatabase database, final String schema) throws Exception {
    // MondoDb doesn't support schemas
    return discoverInternal(database);
  }

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(final MongoDatabase database,
                                                          final List<TableInfo<CommonField<BsonType>>> tableInfos) {
    return tableInfos.stream()
        .collect(Collectors.toMap(
            TableInfo::getName,
            TableInfo::getPrimaryKeys));
  }

  @Override
  protected String getQuoteString() {
    return "";
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(final MongoDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final SyncMode syncMode,
                                                               final Optional<String> cursorField) {
    return queryTable(database, columnNames, tableName, null);
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(final MongoDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final CursorInfo cursorInfo,
                                                               final BsonType cursorFieldType) {
    final Bson greaterComparison = gt(cursorInfo.getCursorField(), MongoUtils.getBsonValue(cursorFieldType, cursorInfo.getCursor()));
    return queryTable(database, columnNames, tableName, greaterComparison);
  }

  @Override
  public boolean isCursorType(final BsonType bsonType) {
    // while reading from mongo primary key "id" is always added, so there will be no situation
    // when we have no cursor field here, at least id could be used as cursor here.
    // This logic will be used feather when we will implement part which will show only list of possible
    // cursor fields on UI
    return MongoUtils.ALLOWED_CURSOR_TYPES.contains(bsonType);
  }

  private AutoCloseableIterator<JsonNode> queryTable(final MongoDatabase database,
                                                     final List<String> columnNames,
                                                     final String tableName,
                                                     final Bson filter) {
    final AirbyteStreamNameNamespacePair airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, null);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.read(tableName, columnNames, Optional.ofNullable(filter));
        return AutoCloseableIterators.fromStream(stream, airbyteStream);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  private String buildConnectionString(final JsonNode config, final String credentials) {
    final StringBuilder connectionStrBuilder = new StringBuilder();

    final JsonNode instanceConfig = config.get(MongoUtils.INSTANCE_TYPE);
    final MongoInstanceType instance = MongoInstanceType.fromValue(instanceConfig.get(MongoUtils.INSTANCE).asText());
    switch (instance) {
      case STANDALONE -> {
        connectionStrBuilder.append(
            String.format(MongoUtils.MONGODB_SERVER_URL, credentials, instanceConfig.get(JdbcUtils.HOST_KEY).asText(),
                instanceConfig.get(JdbcUtils.PORT_KEY).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText(),
                config.get(MongoUtils.AUTH_SOURCE).asText(), MongoUtils.tlsEnabledForStandaloneInstance(config, instanceConfig)));
      }
      case REPLICA -> {
        connectionStrBuilder.append(
            String.format(MongoUtils.MONGODB_REPLICA_URL, credentials, instanceConfig.get(MongoUtils.SERVER_ADDRESSES).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText(),
                config.get(MongoUtils.AUTH_SOURCE).asText()));
        if (instanceConfig.has(MongoUtils.REPLICA_SET)) {
          connectionStrBuilder.append(String.format("&replicaSet=%s", instanceConfig.get(MongoUtils.REPLICA_SET).asText()));
        }
      }
      case ATLAS -> {
        connectionStrBuilder.append(
            String.format(MongoUtils.MONGODB_CLUSTER_URL, credentials,
                instanceConfig.get(MongoUtils.CLUSTER_URL).asText(), config.get(JdbcUtils.DATABASE_KEY).asText(),
                config.get(MongoUtils.AUTH_SOURCE).asText()));
      }
      default -> throw new IllegalArgumentException("Unsupported instance type: " + instance);
    }
    return connectionStrBuilder.toString();
  }

  @Override
  public void close() throws Exception {}

}
