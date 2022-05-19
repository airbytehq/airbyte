/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static com.mongodb.client.model.Filters.gt;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.AbstractDbSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaType;
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

  private static final String MONGODB_SERVER_URL = "mongodb://%s%s:%s/%s?authSource=%s&ssl=%s";
  private static final String MONGODB_CLUSTER_URL = "mongodb+srv://%s%s/%s?authSource=%s&retryWrites=true&w=majority&tls=true";
  private static final String MONGODB_REPLICA_URL = "mongodb://%s%s/%s?authSource=%s&directConnection=false&ssl=true";
  private static final String USER = "user";
  private static final String PASSWORD = "password";
  private static final String INSTANCE_TYPE = "instance_type";
  private static final String INSTANCE = "instance";
  private static final String HOST = "host";
  private static final String PORT = "port";
  private static final String CLUSTER_URL = "cluster_url";
  private static final String DATABASE = "database";
  private static final String SERVER_ADDRESSES = "server_addresses";
  private static final String REPLICA_SET = "replica_set";
  private static final String AUTH_SOURCE = "auth_source";
  private static final String TLS = "tls";
  private static final String PRIMARY_KEY = "_id";

  public static void main(final String[] args) throws Exception {
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final var credentials = config.has(USER) && config.has(PASSWORD)
        ? String.format("%s:%s@", config.get(USER).asText(), config.get(PASSWORD).asText())
        : StringUtils.EMPTY;

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("connectionString", buildConnectionString(config, credentials))
        .put("database", config.get(DATABASE).asText())
        .build());
  }

  @Override
  protected MongoDatabase createDatabase(final JsonNode config) throws Exception {
    final var dbConfig = toDatabaseConfig(config);
    return new MongoDatabase(dbConfig.get("connectionString").asText(),
        dbConfig.get("database").asText());
  }

  @Override
  public List<CheckedConsumer<MongoDatabase, Exception>> getCheckOperations(final JsonNode config)
      throws Exception {
    final List<CheckedConsumer<MongoDatabase, Exception>> checkList = new ArrayList<>();
    checkList.add(database -> {
      if (getAuthorizedCollections(database).isEmpty()) {
        throw new Exception("Unable to execute any operation on the source!");
      } else {
        LOGGER.info("The source passed the basic operation test!");
      }
    });
    return checkList;
  }

  @Override
  protected JsonSchemaType getType(final BsonType fieldType) {
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

    for (final String collectionName : getAuthorizedCollections(database)) {
      final MongoCollection<Document> collection = database.getCollection(collectionName);
      final List<CommonField<BsonType>> fields = MongoUtils.getUniqueFields(collection).stream().map(MongoUtils::nodeToCommonField).toList();

      // The field name _id is reserved for use as a primary key;
      final TableInfo<CommonField<BsonType>> tableInfo = TableInfo.<CommonField<BsonType>>builder()
          .nameSpace(database.getName())
          .name(collectionName)
          .fields(fields)
          .primaryKeys(List.of(PRIMARY_KEY))
          .build();

      tableInfos.add(tableInfo);
    }
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
                                                               final String tableName) {
    return queryTable(database, columnNames, tableName, null);
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(final MongoDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final String cursorField,
                                                               final BsonType cursorFieldType,
                                                               final String cursor) {
    final Bson greaterComparison = gt(cursorField, MongoUtils.getBsonValue(cursorFieldType, cursor));
    return queryTable(database, columnNames, tableName, greaterComparison);
  }

  private AutoCloseableIterator<JsonNode> queryTable(final MongoDatabase database,
                                                     final List<String> columnNames,
                                                     final String tableName,
                                                     final Bson filter) {
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.read(tableName, columnNames, Optional.ofNullable(filter));
        return AutoCloseableIterators.fromStream(stream);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  private String buildConnectionString(final JsonNode config, final String credentials) {
    final StringBuilder connectionStrBuilder = new StringBuilder();

    final JsonNode instanceConfig = config.get(INSTANCE_TYPE);
    final MongoInstanceType instance = MongoInstanceType.fromValue(instanceConfig.get(INSTANCE).asText());
    switch (instance) {
      case STANDALONE -> {
        // supports backward compatibility and secure only connector
        final var tls = config.has(TLS) ? config.get(TLS).asBoolean() : (instanceConfig.has(TLS) ? instanceConfig.get(TLS).asBoolean() : true);
        connectionStrBuilder.append(
            String.format(MONGODB_SERVER_URL, credentials, instanceConfig.get(HOST).asText(), instanceConfig.get(PORT).asText(),
                config.get(DATABASE).asText(), config.get(AUTH_SOURCE).asText(), tls));
      }
      case REPLICA -> {
        connectionStrBuilder.append(
            String.format(MONGODB_REPLICA_URL, credentials, instanceConfig.get(SERVER_ADDRESSES).asText(), config.get(DATABASE).asText(),
                config.get(AUTH_SOURCE).asText()));
        if (instanceConfig.has(REPLICA_SET)) {
          connectionStrBuilder.append(String.format("&replicaSet=%s", instanceConfig.get(REPLICA_SET).asText()));
        }
      }
      case ATLAS -> {
        connectionStrBuilder.append(
            String.format(MONGODB_CLUSTER_URL, credentials, instanceConfig.get(CLUSTER_URL).asText(), config.get(DATABASE).asText(),
                config.get(AUTH_SOURCE).asText()));
      }
      default -> throw new IllegalArgumentException("Unsupported instance type: " + instance);
    }
    return connectionStrBuilder.toString();
  }

  @Override
  public void close() throws Exception {}
}
