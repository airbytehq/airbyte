/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.*;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.MongoUtil.CollectionStatistics;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteAnalyticsTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.bson.*;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Retrieves iterators used for the initial snapshot
 */
public class InitialSnapshotHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(InitialSnapshotHandler.class);

  /**
   * For each given stream configured as incremental sync it will output an iterator that will
   * retrieve documents from the given database. Each iterator will start after the last checkpointed
   * document, if any, or from the beginning of the stream otherwise.
   */
  public List<AutoCloseableIterator<AirbyteMessage>> getIterators(
                                                                  final List<ConfiguredAirbyteStream> streams,
                                                                  final MongoDbStateManager stateManager,
                                                                  final MongoDatabase database,
                                                                  final MongoDbSourceConfig config,
                                                                  final boolean decorateWithStartedStatus,
                                                                  final boolean decorateWithCompletedStatus,
                                                                  final Instant emittedAt,
                                                                  final Optional<Duration> cdcInitialLoadTimeout) {
    final boolean isEnforceSchema = config.getEnforceSchema();
    final var checkpointInterval = config.getCheckpointInterval();
    final String MULTIPLE_ID_TYPES_ANALYTICS_MESSAGE_KEY = "db-sources-mongo-multiple-id-types";
    LOGGER.info("***getIterators for initial snapshot for streams: {}", streams);
    return streams
        .stream()
        .filter(airbyteStream -> airbyteStream.getStream().getNamespace().equals(database.getName()))
        .map(airbyteStream -> {
          final var collectionName = airbyteStream.getStream().getName();
          final var namespace = airbyteStream.getStream().getNamespace();
          final var collection = database.getCollection(collectionName);
          LOGGER.info("***collection: {}", collection);
          final var fields = Projections.fields(Projections.include(CatalogHelpers.getTopLevelFieldNames(airbyteStream).stream().toList()));
          LOGGER.info("***fields: {}", fields);
          final var idTypes = getIdFieldTypes(collection);
          if (idTypes.size() > 1) {
            LOGGER.warn("The _id fields in this collection are not consistently typed, which may lead to data loss (collection = {}, types = {}).",
                collectionName, idTypes);
            AirbyteTraceMessageUtility
                .emitAnalyticsTrace(new AirbyteAnalyticsTraceMessage().withType(MULTIPLE_ID_TYPES_ANALYTICS_MESSAGE_KEY).withValue("1"));
          }

          idTypes.stream().findFirst().ifPresent(idType -> {
            if (IdType.findByBsonType(idType).isEmpty()) {
              throw new ConfigErrorException("Only _id fields with the following types are currently supported: " + IdType.SUPPORTED
                  + " (collection = " + collectionName + "). type: " + idType);
            }
          });

          // find the existing state, if there is one, for this stream
          final Optional<MongoDbStreamState> existingState =
              stateManager.getStreamState(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());

          final Optional<CollectionStatistics> collectionStatistics = MongoUtil.getCollectionStatistics(database, airbyteStream);
          final var recordIterator = new MongoDbInitialLoadRecordIterator(collection, fields, existingState, isEnforceSchema,
              MongoUtil.getChunkSizeForCollection(collectionStatistics, airbyteStream), emittedAt, cdcInitialLoadTimeout);
          final var stateIterator =
              new SourceStateIterator<>(recordIterator, airbyteStream, stateManager, new StateEmitFrequency(checkpointInterval,
                  MongoConstants.CHECKPOINT_DURATION));
          final var iterator = AutoCloseableIterators.fromIterator(stateIterator, recordIterator::close, null);

          List<AutoCloseableIterator<AirbyteMessage>> itList = Stream.of(iterator).collect(Collectors.toList());
          if (decorateWithStartedStatus) {
            itList.addFirst(new StreamStatusTraceEmitterIterator(
                new AirbyteStreamStatusHolder(new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(collectionName, namespace),
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED)));
          }

          if (decorateWithCompletedStatus) {
            itList.addLast(new StreamStatusTraceEmitterIterator(
                new AirbyteStreamStatusHolder(new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(collectionName, namespace),
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)));
          }
          return (itList.size() == 1) ? iterator : AutoCloseableIterators.concatWithEagerClose(itList);
        })
        .toList();
  }

  /*
   * BSON compares values of different types according to a fixed ordering of type "brackets"
   * (https://www.mongodb.com/docs/manual/reference/bson-type-comparison-order/). Values of the types
   * within a bracket interleave in the _id index, while the brackets themselves occupy contiguous,
   * non-overlapping ranges of the index.
   */
  private static final List<List<String>> TYPE_BRACKETS = List.of(
      List.of("minKey"),
      List.of("null", "undefined"),
      List.of("int", "long", "double", "decimal"),
      List.of("string", "symbol"),
      List.of("object"),
      List.of("array"),
      List.of("binData"),
      List.of("objectId"),
      List.of("bool"),
      List.of("date"),
      List.of("timestamp"),
      List.of("regex"),
      List.of("javascript", "javascriptWithScope"),
      List.of("dbPointer"),
      List.of("maxKey"));

  /**
   * Returns the list of BSON types (as {@code $type} aliases, e.g. "objectId", "string") present in
   * the _id field of the provided collection.
   *
   * Because the mandatory _id index is ordered by type bracket first, the types present can be
   * determined with a constant number of index seeks instead of aggregating over every document (a
   * full collection scan): if the smallest and largest _id share a single-type bracket, every
   * document in between is of that type; otherwise each candidate type is probed with one
   * index-bounded {@code $type} query.
   *
   * @param collection Collection to collect the _id types of.
   * @return List of bson types (as strings) that the _id field contains.
   */
  @VisibleForTesting
  List<String> getIdFieldTypes(final MongoCollection<Document> collection) {
    final BsonType minType = endpointIdType(collection, Sorts.ascending(MongoConstants.ID_FIELD));
    if (minType == null) {
      // empty collection
      return List.of();
    }
    final BsonType maxType = endpointIdType(collection, Sorts.descending(MongoConstants.ID_FIELD));

    final List<String> minBracket = bracketOf(minType);
    final List<String> maxBracket = bracketOf(maxType);
    if (minBracket.equals(maxBracket)) {
      if (minBracket.size() == 1) {
        return minBracket;
      }
      // types within this bracket (e.g. int/long/double/decimal) interleave; probe each member
      return minBracket.stream().filter(alias -> idOfTypeExists(collection, alias)).toList();
    }

    // _id values span multiple brackets; probe every type with one index seek each
    return Stream.concat(
        TYPE_BRACKETS.stream().flatMap(List::stream),
        Stream.of(typeAlias(minType), typeAlias(maxType)))
        .distinct()
        .filter(alias -> idOfTypeExists(collection, alias))
        .toList();
  }

  /**
   * Returns the BSON type of the first _id in the given index order, or null if the collection is
   * empty. This is a covered query: it only touches the _id index and never fetches a document.
   */
  private static BsonType endpointIdType(final MongoCollection<Document> collection, final Bson sort) {
    final BsonDocument document = collection.withDocumentClass(BsonDocument.class)
        .find()
        .projection(Projections.include(MongoConstants.ID_FIELD))
        .sort(sort)
        .limit(1)
        .first();
    return document == null ? null : document.get(MongoConstants.ID_FIELD).getBsonType();
  }

  /**
   * Returns true if at least one document has an _id of the given type. {@code $type} predicates are
   * answered with tight index bounds (MongoDB 4.0+), so this is a single seek on the _id index.
   */
  private static boolean idOfTypeExists(final MongoCollection<Document> collection, final String typeAlias) {
    return collection.find(Filters.type(MongoConstants.ID_FIELD, typeAlias))
        .projection(Projections.include(MongoConstants.ID_FIELD))
        .limit(1)
        .first() != null;
  }

  private static List<String> bracketOf(final BsonType type) {
    final String alias = typeAlias(type);
    return TYPE_BRACKETS.stream()
        .filter(bracket -> bracket.contains(alias))
        .findFirst()
        .orElse(List.of(alias));
  }

  /** Maps a driver {@link BsonType} to the alias used by the {@code $type} operator. */
  private static String typeAlias(final BsonType type) {
    return switch (type) {
      case DOUBLE -> "double";
      case STRING -> "string";
      case DOCUMENT -> "object";
      case ARRAY -> "array";
      case BINARY -> "binData";
      case UNDEFINED -> "undefined";
      case OBJECT_ID -> "objectId";
      case BOOLEAN -> "bool";
      case DATE_TIME -> "date";
      case NULL -> "null";
      case REGULAR_EXPRESSION -> "regex";
      case DB_POINTER -> "dbPointer";
      case JAVASCRIPT -> "javascript";
      case SYMBOL -> "symbol";
      case JAVASCRIPT_WITH_SCOPE -> "javascriptWithScope";
      case INT32 -> "int";
      case TIMESTAMP -> "timestamp";
      case INT64 -> "long";
      case DECIMAL128 -> "decimal";
      case MIN_KEY -> "minKey";
      case MAX_KEY -> "maxKey";
      default -> type.name();
    };
  }

}
