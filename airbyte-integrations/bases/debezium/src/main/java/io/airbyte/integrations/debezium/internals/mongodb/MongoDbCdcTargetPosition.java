/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.Map;
import java.util.Objects;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implementation of the {@link CdcTargetPosition} interface that provides methods for determining
 * when a sync has reached the target position of the CDC log for MongoDB. In this case, the target
 * position is a resume token value from the MongoDB oplog. This implementation compares the
 * timestamp present in the Debezium change event against the timestamp of the resume token recorded
 * at the start of a sync. When the event timestamp exceeds the resume token timestamp, the sync
 * should stop to prevent it from running forever.
 */
public class MongoDbCdcTargetPosition implements CdcTargetPosition<BsonTimestamp> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcTargetPosition.class);

  private final BsonTimestamp resumeTokenTimestamp;

  public MongoDbCdcTargetPosition(final BsonDocument resumeToken) {
    this.resumeTokenTimestamp = ResumeTokens.getTimestamp(resumeToken);
  }

  /**
   * Constructs a new {@link MongoDbCdcTargetPosition} by fetching the most recent resume token from
   * the MongoDB database.
   *
   * @param mongoClient A {@link MongoClient} used to retrieve the resume token.
   * @return The {@link MongoDbCdcTargetPosition} set to the most recent resume token present in the
   *         database.
   */
  public static MongoDbCdcTargetPosition targetPosition(final MongoClient mongoClient) {
    final BsonDocument resumeToken = MongoDbResumeTokenHelper.getResumeToken(mongoClient);
    return new MongoDbCdcTargetPosition(resumeToken);
  }

  @VisibleForTesting
  BsonTimestamp getResumeTokenTimestamp() {
    return resumeTokenTimestamp;
  }

  @Override
  public boolean isHeartbeatSupported() {
    return true;
  }

  @Override
  public boolean reachedTargetPosition(final ChangeEventWithMetadata changeEventWithMetadata) {
    if (changeEventWithMetadata.isSnapshotEvent()) {
      return false;
    } else if (SnapshotMetadata.LAST == changeEventWithMetadata.snapshotMetadata()) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final BsonTimestamp eventResumeTokenTimestamp =
          MongoDbResumeTokenHelper.extractTimestamp(changeEventWithMetadata.eventValueAsJson());
      boolean isEventResumeTokenAfter = resumeTokenTimestamp.compareTo(eventResumeTokenTimestamp) <= 0;
      if (isEventResumeTokenAfter) {
        LOGGER.info("Signalling close because record's event timestamp {} is after target event timestamp {}.",
            eventResumeTokenTimestamp, resumeTokenTimestamp);
      }
      return isEventResumeTokenAfter;
    }
  }

  @Override
  public boolean reachedTargetPosition(final BsonTimestamp positionFromHeartbeat) {
    return positionFromHeartbeat != null && positionFromHeartbeat.compareTo(resumeTokenTimestamp) >= 0;
  }

  @Override
  public BsonTimestamp extractPositionFromHeartbeatOffset(final Map<String, ?> sourceOffset) {
    return ResumeTokens.getTimestamp(
        ResumeTokens.fromData(
            sourceOffset.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE_RESUME_TOKEN).toString()));
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;
    MongoDbCdcTargetPosition that = (MongoDbCdcTargetPosition) o;
    return Objects.equals(resumeTokenTimestamp, that.resumeTokenTimestamp);
  }

  @Override
  public int hashCode() {
    return Objects.hash(resumeTokenTimestamp);
  }

}
