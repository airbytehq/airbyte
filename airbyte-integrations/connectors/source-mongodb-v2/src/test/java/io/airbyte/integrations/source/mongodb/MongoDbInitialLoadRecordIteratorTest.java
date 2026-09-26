/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.state.IdType.idToStringRepresenation;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.mongodb.MongoException;
import com.mongodb.MongoNamespace;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.model.Projections;
import io.airbyte.commons.exceptions.TransientErrorException;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;
import org.bson.BsonBinarySubType;
import org.bson.Document;
import org.bson.UuidRepresentation;
import org.bson.internal.UuidHelper;
import org.bson.types.Binary;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.testcontainers.containers.MongoDBContainer;

class MongoDbInitialLoadRecordIteratorTest {

  private static final String DB_NAME = "airbyte_test";
  private static final String COLLECTION_NAME = "collection1";
  private static final String ID_FIELD = "_id";
  private static final String NAME_FIELD = "name";

  private static MongoDBContainer MONGO_DB;
  private MongoClient mongoClient;

  @BeforeAll
  static void init() {
    MONGO_DB = new MongoDBContainer("mongo:6.0.8");
    MONGO_DB.start();
  }

  @BeforeEach
  void setup() {
    mongoClient = MongoClients.create(MONGO_DB.getConnectionString());
    mongoClient.getDatabase(DB_NAME).drop();
  }

  @AfterEach
  void tearDown() {
    mongoClient.close();
  }

  @AfterAll
  static void cleanup() {
    MONGO_DB.stop();
  }

  private MongoCollection<Document> collection() {
    return mongoClient.getDatabase(DB_NAME).getCollection(COLLECTION_NAME);
  }

  private void insertDocuments(final List<Document> documents) {
    collection().insertMany(documents);
  }

  private MongoDbInitialLoadRecordIterator iterator(final Optional<MongoDbStreamState> existingState,
                                                  final boolean isEnforceSchema,
                                                  final int chunkSize,
                                                  final org.bson.conversions.Bson fields) {
    return new MongoDbInitialLoadRecordIterator(collection(), fields, existingState, isEnforceSchema, chunkSize,
        Instant.now(), Optional.empty());
  }

  private MongoDbInitialLoadRecordIterator iterator(final Optional<MongoDbStreamState> existingState,
                                                  final int chunkSize) {
    return iterator(existingState, true, chunkSize,
        Projections.fields(Projections.include(ID_FIELD, NAME_FIELD)));
  }

  @Test
  void testInitialSyncNoState() {
    final List<Document> docs = List.of(
        new Document(Map.of(ID_FIELD, new ObjectId(), NAME_FIELD, "name1")),
        new Document(Map.of(ID_FIELD, new ObjectId(), NAME_FIELD, "name2")),
        new Document(Map.of(ID_FIELD, new ObjectId(), NAME_FIELD, "name3")),
        new Document(Map.of(ID_FIELD, new ObjectId(), NAME_FIELD, "name4")),
        new Document(Map.of(ID_FIELD, new ObjectId(), NAME_FIELD, "name5")));
    insertDocuments(docs);

    final var iterator = iterator(Optional.empty(), 2);
    assertEquals(Optional.of(new AirbyteStreamNameNamespacePair(COLLECTION_NAME, DB_NAME)), iterator.getAirbyteStream());

    final List<Document> results = new ArrayList<>();
    while (iterator.hasNext()) {
      results.add(iterator.next());
    }

    assertEquals(5, results.size());
    final List<ObjectId> sortedIds = docs.stream().map(d -> d.getObjectId(ID_FIELD)).sorted().toList();
    for (int i = 0; i < 5; i++) {
      assertEquals(sortedIds.get(i), results.get(i).getObjectId(ID_FIELD));
    }
  }

  @Test
  void testInitialSyncNoStateEmptyCollection() {
    final var iterator = iterator(Optional.empty(), 2);
    assertFalse(iterator.hasNext());
  }

  @Test
  void testMultiChunkIteration() {
    final List<Document> docs = new ArrayList<>();
    for (int i = 1; i <= 25; i++) {
      docs.add(new Document(Map.of(ID_FIELD, i, NAME_FIELD, "name" + i)));
    }
    insertDocuments(docs);

    final var iterator = iterator(Optional.empty(), 10);
    final List<Integer> results = new ArrayList<>();
    while (iterator.hasNext()) {
      results.add(iterator.next().getInteger(ID_FIELD));
    }

    assertEquals(25, results.size());
    for (int i = 0; i < 25; i++) {
      assertEquals(i + 1, results.get(i));
    }
  }

  static Stream<Arguments> resumeFromExistingState() {
    final ObjectId objectId2 = new ObjectId("64c0029d95ad260d69ef28a2");
    final ObjectId objectId3 = new ObjectId("64c0029d95ad260d69ef28a3");
    final Binary binary2 = new Binary(Base64.getDecoder().decode("AAAAA2JiYmI="));
    final Binary binary3 = new Binary(Base64.getDecoder().decode("AAAAA2NjY2M="));
    final Binary uuid2 = uuidBinary("8cee6d1e-ce07-4dc9-8bcb-c99c5a163a75");
    final Binary uuid3 = uuidBinary("9cee6d1e-ce07-4dc9-8bcb-c99c5a163a75");
    return Stream.of(
        Arguments.of(
            List.of(new ObjectId("64c0029d95ad260d69ef28a1"), objectId2, objectId3),
            new MongoDbStreamState(idToStringRepresenation(objectId2, IdType.OBJECT_ID),
                InitialSnapshotStatus.IN_PROGRESS, IdType.OBJECT_ID, (byte) 0),
            objectId3),
        Arguments.of(
            List.of("a1", "a2", "a3"),
            new MongoDbStreamState(idToStringRepresenation("a2", IdType.STRING),
                InitialSnapshotStatus.IN_PROGRESS, IdType.STRING, (byte) 0),
            "a3"),
        Arguments.of(
            List.of(1, 2, 3),
            new MongoDbStreamState(idToStringRepresenation(2, IdType.INT),
                InitialSnapshotStatus.IN_PROGRESS, IdType.INT, (byte) 0),
            3),
        Arguments.of(
            List.of(1L, 2L, 3L),
            new MongoDbStreamState(idToStringRepresenation(2L, IdType.LONG),
                InitialSnapshotStatus.IN_PROGRESS, IdType.LONG, (byte) 0),
            3L),
        Arguments.of(
            List.of(new Binary(Base64.getDecoder().decode("AAAAAWFhYWE=")), binary2, binary3),
            new MongoDbStreamState(idToStringRepresenation(binary2, IdType.BINARY),
                InitialSnapshotStatus.IN_PROGRESS, IdType.BINARY, binary2.getType()),
            binary3),
        Arguments.of(
            List.of(uuidBinary("7cee6d1e-ce07-4dc9-8bcb-c99c5a163a75"), uuid2, uuid3),
            new MongoDbStreamState(idToStringRepresenation(uuid2, IdType.BINARY),
                InitialSnapshotStatus.IN_PROGRESS, IdType.BINARY, uuid2.getType()),
            uuid3));
  }

  private static Binary uuidBinary(final String uuid) {
    return new Binary(BsonBinarySubType.UUID_STANDARD,
        UuidHelper.encodeUuidToBinary(UUID.fromString(uuid), UuidRepresentation.STANDARD));
  }

  @ParameterizedTest
  @MethodSource("resumeFromExistingState")
  void testResumeFromExistingState(final List<Object> ids,
                                   final MongoDbStreamState existingState,
                                   final Object expectedId) {
    final List<Document> docs = new ArrayList<>();
    for (int i = 0; i < ids.size(); i++) {
      docs.add(new Document(Map.of(ID_FIELD, ids.get(i), NAME_FIELD, "name" + i)));
    }
    insertDocuments(docs);

    final var iterator = iterator(Optional.of(existingState), 10);
    assertTrue(iterator.hasNext());
    final Document next = iterator.next();
    assertEquals(expectedId, next.get(ID_FIELD));
    assertFalse(iterator.hasNext());
  }

  @Test
  void testSchemalessProjection() {
    insertDocuments(List.of(new Document(Map.of(ID_FIELD, 1, NAME_FIELD, "name1"))));

    final var schemalessIterator =
        iterator(Optional.empty(), false, 10, Projections.fields(Projections.include(ID_FIELD)));
    assertTrue(schemalessIterator.hasNext());
    assertTrue(schemalessIterator.next().containsKey(NAME_FIELD));
    assertFalse(schemalessIterator.hasNext());

    final var enforcedIterator =
        iterator(Optional.empty(), true, 10, Projections.fields(Projections.include(ID_FIELD)));
    assertTrue(enforcedIterator.hasNext());
    assertFalse(enforcedIterator.next().containsKey(NAME_FIELD));
    assertFalse(enforcedIterator.hasNext());
  }

  private record MockFind(MongoCollection<Document> collection, FindIterable<Document> findIterable) {}

  @SuppressWarnings("unchecked")
  private MockFind mockFind() {
    final MongoCollection<Document> collection = mock(MongoCollection.class);
    final FindIterable<Document> findIterable = mock(FindIterable.class);
    when(collection.find()).thenReturn(findIterable);
    when(findIterable.filter(any())).thenReturn(findIterable);
    when(findIterable.projection(any())).thenReturn(findIterable);
    when(findIterable.limit(anyInt())).thenReturn(findIterable);
    when(findIterable.sort(any())).thenReturn(findIterable);
    when(findIterable.allowDiskUse(anyBoolean())).thenReturn(findIterable);
    return new MockFind(collection, findIterable);
  }

  @SuppressWarnings("unchecked")
  private MongoCursor<Document> mockCursor(final List<Document> docs) {
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    if (docs.isEmpty()) {
      when(cursor.hasNext()).thenReturn(false);
    } else {
      // hasNext() is called once per document plus once that returns false.
      final Boolean[] tail = new Boolean[docs.size()];
      java.util.Arrays.fill(tail, true);
      tail[docs.size() - 1] = false;
      when(cursor.hasNext()).thenReturn(true, tail);
      final Document[] rest = docs.subList(1, docs.size()).toArray(new Document[0]);
      when(cursor.next()).thenReturn(docs.get(0), rest);
    }
    return cursor;
  }

  @Test
  void testCdcInitialLoadTimeoutWithStream() {
    final MockFind mockFind = mockFind();
    when(mockFind.collection().getNamespace()).thenReturn(new MongoNamespace("db", "coll"));

    final var iterator = new MongoDbInitialLoadRecordIterator(mockFind.collection(),
        Projections.include(ID_FIELD), Optional.empty(), true, 10,
        Instant.now().minus(Duration.ofMinutes(10)), Optional.of(Duration.ofMinutes(1)));

    final TransientErrorException exception = assertThrows(TransientErrorException.class, iterator::hasNext);
    assertTrue(exception.getMessage().contains("db"));
    assertTrue(exception.getMessage().contains("coll"));
    assertTrue(exception.getMessage().contains(Duration.ofMinutes(1).toString()));
    verify(mockFind.collection(), never()).find();
  }

  @Test
  void testCdcInitialLoadTimeoutWithoutStream() {
    final MockFind mockFind = mockFind();
    when(mockFind.collection().getNamespace()).thenReturn(null);

    final var iterator = new MongoDbInitialLoadRecordIterator(mockFind.collection(),
        Projections.include(ID_FIELD), Optional.empty(), true, 10,
        Instant.now().minus(Duration.ofMinutes(10)), Optional.of(Duration.ofMinutes(1)));

    final TransientErrorException exception = assertThrows(TransientErrorException.class, iterator::hasNext);
    assertTrue(exception.getMessage().contains("<unknown stream>"));
  }

  @Test
  void testNoTimeoutWhenWithinLimit() {
    final MockFind mockFind = mockFind();
    final Document doc = new Document(ID_FIELD, new ObjectId());
    final MongoCursor<Document> cursor = mockCursor(List.of(doc));
    when(mockFind.findIterable().cursor()).thenReturn(cursor);

    final var iterator = new MongoDbInitialLoadRecordIterator(mockFind.collection(),
        Projections.include(ID_FIELD), Optional.empty(), true, 10,
        Instant.now(), Optional.of(Duration.ofHours(1)));

    assertTrue(iterator.hasNext());
    assertEquals(doc, iterator.next());
  }

  @Test
  void testFailureBuildingNextSubqueryPropagates() {
    final MockFind mockFind1 = mockFind();
    final MockFind mockFind2 = mockFind();
    final MongoCollection<Document> collection = mockFind1.collection();
    when(collection.find()).thenReturn(mockFind1.findIterable(), mockFind2.findIterable());

    final MongoCursor<Document> cursor1 = mockCursor(List.of(new Document(ID_FIELD, new ObjectId())));
    when(mockFind1.findIterable().cursor()).thenReturn(cursor1);
    when(mockFind2.findIterable().cursor()).thenThrow(new MongoException("boom"));

    final var iterator = new MongoDbInitialLoadRecordIterator(collection,
        Projections.include(ID_FIELD), Optional.empty(), true, 10,
        Instant.now(), Optional.empty());

    assertTrue(iterator.hasNext());
    assertEquals(1, iterator.next().size());
    assertThrows(MongoException.class, iterator::hasNext);
    verify(cursor1).close();
  }

  @Test
  void testFailureClosingCursorPropagates() {
    final MockFind mockFind = mockFind();
    final MongoCursor<Document> cursor1 = mockCursor(List.of(new Document(ID_FIELD, new ObjectId())));
    when(mockFind.findIterable().cursor()).thenReturn(cursor1);
    doThrow(new MongoException("close failed")).when(cursor1).close();

    final var iterator = new MongoDbInitialLoadRecordIterator(mockFind.collection(),
        Projections.include(ID_FIELD), Optional.empty(), true, 10,
        Instant.now(), Optional.empty());

    assertTrue(iterator.hasNext());
    iterator.next();
    assertThrows(MongoException.class, iterator::hasNext);
  }

  @Test
  void testEndOfDataWhenNextSubqueryEmpty() {
    final MockFind mockFind1 = mockFind();
    final MockFind mockFind2 = mockFind();
    final MongoCollection<Document> collection = mockFind1.collection();
    when(collection.find()).thenReturn(mockFind1.findIterable(), mockFind2.findIterable());

    final Document doc = new Document(ID_FIELD, new ObjectId());
    final MongoCursor<Document> cursor1 = mockCursor(List.of(doc));
    final MongoCursor<Document> cursor2 = mockCursor(List.of());
    when(mockFind1.findIterable().cursor()).thenReturn(cursor1);
    when(mockFind2.findIterable().cursor()).thenReturn(cursor2);

    final var iterator = new MongoDbInitialLoadRecordIterator(collection,
        Projections.include(ID_FIELD), Optional.empty(), true, 10,
        Instant.now(), Optional.empty());

    assertTrue(iterator.hasNext());
    assertEquals(doc, iterator.next());
    assertFalse(iterator.hasNext());
  }

}
