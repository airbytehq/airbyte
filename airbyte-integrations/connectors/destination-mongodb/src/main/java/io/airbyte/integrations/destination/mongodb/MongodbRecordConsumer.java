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

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.bson.Document;
import org.joda.time.LocalDateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbRecordConsumer.class);

  private static final String AIRBYTE_DATA = "_airbyte_data";
  private static final String AIRBYTE_EMITTED_AT = "_airbyte_emitted_at";

  private final Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs;
  private final MongoDatabase mongoDatabase;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final ObjectMapper objectMapper;

  private AirbyteMessage lastStateMessage = null;

  public MongodbRecordConsumer(Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs,
                               MongoDatabase mongoDatabase,
                               ConfiguredAirbyteCatalog catalog,
                               Consumer<AirbyteMessage> outputRecordCollector) {
    this.writeConfigs = writeConfigs;
    this.mongoDatabase = mongoDatabase;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.objectMapper = new ObjectMapper();
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.STATE) {
      lastStateMessage = message;
    } else if (message.getType() == AirbyteMessage.Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();
      AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);

      if (!writeConfigs.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
      }
      try {
        Map<String, Object> result = objectMapper.convertValue(recordMessage.getData(), new TypeReference<>() {});
        var newDocument = new Document();
        newDocument.put(AIRBYTE_DATA, new Document(result));
        newDocument.put(AIRBYTE_EMITTED_AT, new LocalDateTime().toString());

        var writeConfig = writeConfigs.get(pair);
        var collection = writeConfig.getCollection();

        var documents = writeConfig.getDocuments();
        if (!documents.contains(newDocument.get(AIRBYTE_DATA, Document.class))) {
          collection.insertOne(newDocument);
        }
      } catch (RuntimeException e) {
        LOGGER.error("Got an error while writing message:" + e.getMessage());
        throw new RuntimeException(e);
      }
    }
  }

  @Override
  protected void close(boolean hasFailed) {
    try {
      if (!hasFailed) {
        LOGGER.info("Migration finished with no explicit errors. Copying data from tmp tables to permanent");
        writeConfigs.values()
            .forEach(
                mongodbWriteConfig -> copyTable(mongoDatabase, mongodbWriteConfig.getCollectionName(),
                    mongodbWriteConfig.getTmpCollectionName()));
        outputRecordCollector.accept(lastStateMessage);
      } else {
        LOGGER.warn("Had errors while migrations");
      }
    } finally {
      LOGGER.info("Removing tmp tables...");
      writeConfigs.values()
          .forEach(mongodbWriteConfig -> mongoDatabase.getCollection(mongodbWriteConfig.getTmpCollectionName()).drop());
      LOGGER.info("Finishing destination process...completed");
    }
  }

  /* Helpers */

  private static void copyTable(MongoDatabase mongoDatabase, String collectionName, String tmpCollectionName) {

    var tempCollection = getOrCreateNewMongodbCollection(mongoDatabase, tmpCollectionName);
    var collection = getOrCreateNewMongodbCollection(mongoDatabase, collectionName);
    List<Document> documents = new ArrayList<>();
    try (MongoCursor<Document> cursor = tempCollection.find().projection(excludeId()).iterator()) {
      while (cursor.hasNext()) {
        documents.add(cursor.next());
      }
    }
    if (!documents.isEmpty()) {
      collection.insertMany(documents);
    }
  }

  private static MongoCollection<Document> getOrCreateNewMongodbCollection(MongoDatabase database, String collectionName) {
    var collectionNames = StreamSupport
        .stream(database.listCollectionNames().spliterator(), false)
        .collect(Collectors.toSet());
    if (!collectionNames.contains(collectionName)) {
      database.createCollection(collectionName);
    }
    return database.getCollection(collectionName);
  }

}
