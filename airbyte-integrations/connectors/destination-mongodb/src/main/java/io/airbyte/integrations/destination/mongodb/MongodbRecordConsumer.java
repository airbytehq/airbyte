/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.apache.commons.codec.digest.DigestUtils;
import org.bson.Document;
import org.joda.time.LocalDateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbRecordConsumer.class);

  private static final String AIRBYTE_DATA = "_airbyte_data";
  private static final String AIRBYTE_DATA_HASH = "_airbyte_data_hash";
  private static final String AIRBYTE_EMITTED_AT = "_airbyte_emitted_at";

  private final Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs;
  private final MongoDatabase mongoDatabase;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final ObjectMapper objectMapper;

  private AirbyteMessage lastStateMessage = null;

  public MongodbRecordConsumer(final Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs,
                               final MongoDatabase mongoDatabase,
                               final ConfiguredAirbyteCatalog catalog,
                               final Consumer<AirbyteMessage> outputRecordCollector) {
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
  protected void acceptTracked(final AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.STATE) {
      lastStateMessage = message;
    } else if (message.getType() == AirbyteMessage.Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();
      final AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);

      if (!writeConfigs.containsKey(pair)) {
        LOGGER.error("Message contained record from a stream that was not in the catalog. catalog: {}, message: {}",
            Jsons.serialize(catalog), Jsons.serialize(recordMessage));
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
      }
      final var writeConfig = writeConfigs.get(pair);
      insertRecordToTmpCollection(writeConfig, message);
    }
  }

  @Override
  protected void close(final boolean hasFailed) {
    try {
      if (!hasFailed) {
        LOGGER.info("Migration finished with no explicit errors. Copying data from tmp tables to permanent");
        writeConfigs.values().forEach(mongodbWriteConfig -> Exceptions.toRuntime(() -> {
          try {
            copyTable(mongoDatabase, mongodbWriteConfig.getCollectionName(), mongodbWriteConfig.getTmpCollectionName());
          } catch (final RuntimeException e) {
            LOGGER.error("Failed to process a message for Streams numbers: {}, SyncMode: {}, CollectionName: {}, TmpCollectionName: {}",
                catalog.getStreams().size(), mongodbWriteConfig.getSyncMode(), mongodbWriteConfig.getCollectionName(),
                mongodbWriteConfig.getTmpCollectionName());
            LOGGER.error("Failed with exception: {}", e.getMessage());
            throw new RuntimeException(e);
          }
        }));
        outputRecordCollector.accept(lastStateMessage);
      } else {
        LOGGER.error("Had errors while migrations");
      }
    } finally {
      LOGGER.info("Removing tmp collections...");
      writeConfigs.values()
          .forEach(mongodbWriteConfig -> mongoDatabase.getCollection(mongodbWriteConfig.getTmpCollectionName()).drop());
      LOGGER.info("Finishing destination process...completed");
    }
  }

  /* Helpers */

  private void insertRecordToTmpCollection(final MongodbWriteConfig writeConfig,
                                           final AirbyteMessage message) {
    try {
      final AirbyteRecordMessage recordMessage = message.getRecord();
      final Map<String, Object> result = objectMapper.convertValue(recordMessage.getData(), new TypeReference<>() {});
      final var newDocumentDataHashCode = UUID.nameUUIDFromBytes(DigestUtils.md5Hex(Jsons.toBytes(recordMessage.getData())).getBytes(
          Charset.defaultCharset())).toString();
      final var newDocument = new Document();
      newDocument.put(AIRBYTE_DATA, new Document(result));
      newDocument.put(AIRBYTE_DATA_HASH, newDocumentDataHashCode);
      newDocument.put(AIRBYTE_EMITTED_AT, new LocalDateTime().toString());

      final var collection = writeConfig.getCollection();

      final var documentsHash = writeConfig.getDocumentsHash();
      if (!documentsHash.contains(newDocumentDataHashCode)) {
        collection.insertOne(newDocument);
        documentsHash.add(newDocumentDataHashCode);
      } else {
        LOGGER.info("Object with hashCode = {} already exist in table {}.", newDocumentDataHashCode, writeConfig.getCollectionName());
      }
    } catch (final RuntimeException e) {
      LOGGER.error("Got an error while writing message:" + e.getMessage());
      LOGGER.error(String.format(
          "Failed to process a message for Streams numbers: %s, SyncMode: %s, CollectionName: %s, TmpCollectionName: %s, AirbyteMessage: %s",
          catalog.getStreams().size(), writeConfig.getSyncMode(), writeConfig.getCollectionName(), writeConfig.getTmpCollectionName(), message));
      throw new RuntimeException(e);
    }
  }

  private static void copyTable(final MongoDatabase mongoDatabase, final String collectionName, final String tmpCollectionName) {

    final var tempCollection = mongoDatabase.getOrCreateNewCollection(tmpCollectionName);
    final var collection = mongoDatabase.getOrCreateNewCollection(collectionName);
    final List<Document> documents = new ArrayList<>();
    try (final MongoCursor<Document> cursor = tempCollection.find().projection(excludeId()).iterator()) {
      while (cursor.hasNext()) {
        documents.add(cursor.next());
      }
    }
    if (!documents.isEmpty()) {
      collection.insertMany(documents);
    }
  }

}
