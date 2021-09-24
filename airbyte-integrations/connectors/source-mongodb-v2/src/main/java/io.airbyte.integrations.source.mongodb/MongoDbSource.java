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
import io.airbyte.db.Databases;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.AbstractDbSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
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
  private static final String HOST = "host";
  private static final String PORT = "port";
  private static final String CLUSTER_URL = "cluster_url";
  private static final String DATABASE = "database";
  private static final String SERVER_ADDRESSES = "server_addresses";
  private static final String REPLICA_SET = "replica_set";
  private static final String AUTH_SOURCE = "auth_source";
  private static final String TLS = "tls";
  private static final String PRIMARY_KEY = "_id";

  public static void main(String[] args) throws Exception {
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    var credentials = config.has(USER) && config.has(PASSWORD)
        ? String.format("%s:%s@", config.get(USER).asText(), config.get(PASSWORD).asText())
        : StringUtils.EMPTY;

    StringBuilder connectionStrBuilder = new StringBuilder();
    JsonNode instanceConfig = config.get(INSTANCE_TYPE);
    if (instanceConfig.has(HOST) && instanceConfig.has(PORT)) {
      // Standalone MongoDb Instance
      var tls = config.has(TLS) ? config.get(TLS).asBoolean() : instanceConfig.get(TLS).asBoolean(); // for backward compatibility
      connectionStrBuilder.append(String.format(MONGODB_SERVER_URL, credentials, instanceConfig.get(HOST).asText(), instanceConfig.get(PORT).asText(),
          config.get(DATABASE).asText(), config.get(AUTH_SOURCE).asText(), tls));
    } else if (instanceConfig.has(CLUSTER_URL)) {
      // MongoDB Atlas
      connectionStrBuilder.append(
          String.format(MONGODB_CLUSTER_URL, credentials, instanceConfig.get(CLUSTER_URL).asText(), config.get(DATABASE).asText(),
              config.get(AUTH_SOURCE).asText()));
    } else {
      // Replica Set & Shard
      connectionStrBuilder.append(
          String.format(MONGODB_REPLICA_URL, credentials, instanceConfig.get(SERVER_ADDRESSES).asText(), config.get(DATABASE).asText(),
              config.get(AUTH_SOURCE).asText()));
      if (instanceConfig.has(REPLICA_SET)) {
        connectionStrBuilder.append(String.format("&replicaSet=%s", instanceConfig.get(REPLICA_SET).asText()));
      }
    }

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("connectionString", connectionStrBuilder.toString())
        .put("database", config.get(DATABASE).asText())
        .build());
  }

  @Override
  protected MongoDatabase createDatabase(JsonNode config) throws Exception {
    var dbConfig = toDatabaseConfig(config);
    return Databases.createMongoDatabase(dbConfig.get("connectionString").asText(),
        dbConfig.get("database").asText());
  }

  @Override
  public List<CheckedConsumer<MongoDatabase, Exception>> getCheckOperations(JsonNode config)
      throws Exception {
    List<CheckedConsumer<MongoDatabase, Exception>> checkList = new ArrayList<>();
    checkList.add(database -> {
      if (database.getCollectionNames() == null || database.getCollectionNames().first() == null) {
        throw new Exception("Unable to execute any operation on the source!");
      } else {
        LOGGER.info("The source passed the basic operation test!");
      }
    });
    return checkList;
  }

  @Override
  protected JsonSchemaPrimitive getType(BsonType fieldType) {
    return MongoUtils.getType(fieldType);
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.emptySet();
  }

  @Override
  protected List<TableInfo<CommonField<BsonType>>> discoverInternal(MongoDatabase database)
      throws Exception {
    List<TableInfo<CommonField<BsonType>>> tableInfos = new ArrayList<>();

    for (String collectionName : database.getCollectionNames()) {
      MongoCollection<Document> collection = database.getCollection(collectionName);
      Map<String, BsonType> uniqueFields = MongoUtils.getUniqueFields(collection);

      List<CommonField<BsonType>> fields = uniqueFields.keySet().stream()
          .map(field -> new CommonField<>(field, uniqueFields.get(field)))
          .collect(Collectors.toList());

      // The field name _id is reserved for use as a primary key;
      TableInfo<CommonField<BsonType>> tableInfo = TableInfo.<CommonField<BsonType>>builder()
          .nameSpace(database.getName())
          .name(collectionName)
          .fields(fields)
          .primaryKeys(List.of(PRIMARY_KEY))
          .build();

      tableInfos.add(tableInfo);
    }
    return tableInfos;
  }

  @Override
  protected List<TableInfo<CommonField<BsonType>>> discoverInternal(MongoDatabase database, String schema) throws Exception {
    // MondoDb doesn't support schemas
    return discoverInternal(database);
  }

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(MongoDatabase database,
                                                          List<TableInfo<CommonField<BsonType>>> tableInfos) {
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
  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(MongoDatabase database,
                                                               List<String> columnNames,
                                                               String schemaName,
                                                               String tableName) {
    return queryTable(database, columnNames, tableName, null);
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(MongoDatabase database,
                                                               List<String> columnNames,
                                                               String schemaName,
                                                               String tableName,
                                                               String cursorField,
                                                               BsonType cursorFieldType,
                                                               String cursor) {
    Bson greaterComparison = gt(cursorField, MongoUtils.getBsonValue(cursorFieldType, cursor));
    return queryTable(database, columnNames, tableName, greaterComparison);
  }

  private AutoCloseableIterator<JsonNode> queryTable(MongoDatabase database, List<String> columnNames, String tableName, Bson filter) {
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.read(tableName, columnNames, Optional.ofNullable(filter));
        return AutoCloseableIterators.fromStream(stream);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

}
