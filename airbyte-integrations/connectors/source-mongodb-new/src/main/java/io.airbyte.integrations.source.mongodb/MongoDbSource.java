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

package io.airbyte.integrations.source.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.bson.Document;
import org.jooq.DataType;
import org.jooq.impl.DefaultDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbSource extends AbstractDbSource<DataType, MongoDatabase> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbSource.class);

  private static final String PRIMARY_KEY = "_id";

  private String quote = "";

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    String connectionString = String.format("mongodb://%s:%s@%s:%s/?authSource=%s",
        config.get("user").asText(),
        config.get("password").asText(),
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("auth_source").asText());

    String options = config.has("replicaSet") ? String.format("&replicaSet=%s&tls=true",
        config.get("replicaSet").asText()) : String.format("&tls=%s", config.get("tls").asText());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("connectionString", connectionString + options)
        .put("database", config.get("database").asText())
        .build());
  }

  @Override
  protected MongoDatabase createDatabase(JsonNode config) throws Exception {
    return Databases.createMongoDatabase(config.get("connectionString").asText(),
        config.get("database").asText());
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
  protected JsonSchemaPrimitive getType(DataType fieldType) {
    return MongoUtils.getType(fieldType);
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.emptySet();
  }

  @Override
  protected List<TableInfo<CommonField<DataType>>> discoverInternal(MongoDatabase database)
      throws Exception {
    List<TableInfo<CommonField<DataType>>> tableInfos = new ArrayList<>();

    for (String collectionName : database.getCollectionNames()) {
      MongoCollection<Document> collection = database.getCollection(collectionName);

      MongoCursor<Document> cursor = collection.find().iterator();

      List<CommonField<DataType>> fields = new ArrayList<>();
      Map<String, DataType> uniqueFields = new HashMap<>();
      while (cursor.hasNext()) {
        Document document = cursor.next();
        for (Map.Entry<String, Object> docField : document.entrySet()) {
          DataType dataType = DefaultDataType.getDefaultDataType("String");
          
          fields.add(new CommonField<DataType>(docField.getKey(), dataType));
        }
      }

      // The field name _id is reserved for use as a primary key; its value must be unique in the
      // collection,
      // is immutable, and may be of any type other than an array.
      // map to airbyte schema
      TableInfo<CommonField<DataType>> tableInfo = TableInfo.<CommonField<DataType>>builder()
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
  protected Map<String, List<String>> discoverPrimaryKeys(MongoDatabase database,
      List<TableInfo<CommonField<DataType>>> tableInfos) {

    return tableInfos.stream()
        .collect(Collectors.toMap(
            tableInfo -> tableInfo.getName(),
            tableInfo -> tableInfo.getPrimaryKeys()));
  }

  @Override
  protected String getQuoteString() {
    return quote;
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(MongoDatabase database,
      List<String> columnNames,
      String schemaName,
      String tableName) {

    MongoCollection<Document> collection = database.getCollection(tableName);
    MongoCursor<Document> cursor = collection.find().iterator();
    List<JsonNode> nodes = new ArrayList<>();
    while (cursor.hasNext()) {
      // todo read and map
      ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      nodes.add(jsonNode);
    }
    return AutoCloseableIterators.fromStream(nodes.stream());
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(MongoDatabase database,
      List<String> columnNames,
      String schemaName,
      String tableName,
      String cursorField,
      DataType cursorFieldType,
      String cursor) {

    MongoCollection<Document> collection = database.getCollection(tableName);
    MongoCursor<Document> mongoCursor = collection.find().iterator(); //todo add find query
    List<JsonNode> nodes = new ArrayList<>();
    while (mongoCursor.hasNext()) {
      // todo read and map
      ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      nodes.add(jsonNode);
    }
    return AutoCloseableIterators.fromStream(nodes.stream());
  }

  public static void main(String[] args) throws Exception {
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

}
