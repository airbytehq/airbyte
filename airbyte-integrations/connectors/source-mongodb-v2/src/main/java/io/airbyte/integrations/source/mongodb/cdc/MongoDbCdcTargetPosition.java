/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.SnapshotMetadata;
import io.airbyte.commons.json.Jsons;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.Map;
import java.util.Objects;
import javax.annotation.Nullable;
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
          MongoDbResumeTokenHelper.extractTimestampFromEvent(changeEventWithMetadata.eventValueAsJson());
      final boolean isEventResumeTokenAfter = resumeTokenTimestamp.compareTo(eventResumeTokenTimestamp) <= 0;
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
  public boolean isEventAheadOffset(final Map<String, String> offset, final ChangeEventWithMetadata event) {
    if (offset.size() != 1) {
      return false;
    }

    return MongoDbResumeTokenHelper.extractTimestampFromEvent(event.eventValueAsJson()).getValue() >= ResumeTokens
        .getTimestamp(ResumeTokens.fromData(getResumeToken(offset))).getValue();
  }

  @Override
  public boolean isSameOffset(@Nullable final Map<String, String> offsetA, @Nullable final Map<String, String> offsetB) {
    if (offsetA == null || offsetA.size() != 1) {
      return false;
    }
    if (offsetB == null || offsetB.size() != 1) {
      return false;
    }

    return getResumeToken(offsetA).equals(getResumeToken(offsetB));
  }

  private static String getResumeToken(final Map<String, String> offset) {
    final JsonNode offsetJson = Jsons.deserialize((String) offset.values().toArray()[0]);
    return offsetJson.get(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN).asText();
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;
    final MongoDbCdcTargetPosition that = (MongoDbCdcTargetPosition) o;
    return Objects.equals(resumeTokenTimestamp, that.resumeTokenTimestamp);
  }

  @Override
  public int hashCode() {
    return Objects.hash(resumeTokenTimestamp);
  }

}
