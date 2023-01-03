/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.keen;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.joestelmach.natty.Parser;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is used for timestamp inference. Keen leverages use of time-related data for it's
 * analytics, so it's important to have timestamp values for historical data if possible. If stream
 * contains cursor field, then its value is used as a timestamp, if parsing it is possible.
 */
public class KeenTimestampService {

  private static final Logger LOGGER = LoggerFactory.getLogger(KeenRecordsConsumer.class);

  private static final long SECONDS_FROM_EPOCH_THRESHOLD = 1_000_000_000L;

  private static final long MILLIS_FROM_EPOCH_THRESHOLD = 10_000_000_000L;

  // Map containing stream names paired with their cursor fields
  private Map<String, List<String>> streamCursorFields;
  private final Parser parser;
  private final boolean timestampInferenceEnabled;

  public KeenTimestampService(final ConfiguredAirbyteCatalog catalog, final boolean timestampInferenceEnabled) {
    this.streamCursorFields = new HashMap<>();
    this.parser = new Parser();
    this.timestampInferenceEnabled = timestampInferenceEnabled;

    if (timestampInferenceEnabled) {
      LOGGER.info("Initializing KeenTimestampService, finding cursor fields.");
      streamCursorFields = catalog.getStreams()
          .stream()
          .filter(stream -> stream.getCursorField().size() > 0)
          .map(s -> Pair.of(s.getStream().getName(), s.getCursorField()))
          .collect(Collectors.toMap(Pair::getKey, Pair::getValue));
    }
  }

  /**
   * Tries to inject keen.timestamp field to the given message data. If the stream contains cursor
   * field, it's value is tried to be parsed to timestamp. If this procedure fails, stream is removed
   * from timestamp-parsable stream map, so parsing is not tried for future messages in the same
   * stream. If parsing succeeds, keen.timestamp field is put as a JSON node to the message data and
   * whole data is returned. Otherwise, keen.timestamp is set to emittedAt value
   *
   * @param message AirbyteRecordMessage containing record data
   * @return Record data together with keen.timestamp field
   */
  public JsonNode injectTimestamp(final AirbyteRecordMessage message) {
    final String streamName = message.getStream();
    final List<String> cursorField = streamCursorFields.get(streamName);
    final JsonNode data = message.getData();
    if (timestampInferenceEnabled && cursorField != null) {
      try {
        final String timestamp = parseTimestamp(cursorField, data);
        injectTimestamp(data, timestamp);
      } catch (final Exception e) {
        // If parsing of timestamp has failed, remove stream from timestamp-parsable stream map,
        // so it won't be parsed for future messages.
        LOGGER.info("Unable to parse cursor field: {} into a keen.timestamp", cursorField);
        streamCursorFields.remove(streamName);
        injectTimestamp(data, Instant.ofEpochMilli(message.getEmittedAt()).toString());
      }
    } else {
      injectTimestamp(data, Instant.ofEpochMilli(message.getEmittedAt()).toString());
    }
    return data;
  }

  private void injectTimestamp(final JsonNode data, final String timestamp) {
    final ObjectNode root = ((ObjectNode) data);
    root.set("keen", JsonNodeFactory.instance.objectNode().put("timestamp", timestamp));
  }

  private String parseTimestamp(final List<String> cursorField, final JsonNode data) {
    final JsonNode timestamp = getNestedNode(data, cursorField);
    final long numberTimestamp = timestamp.asLong();
    // if cursor value is below given threshold, assume that it's not epoch timestamp but ordered id
    if (numberTimestamp >= SECONDS_FROM_EPOCH_THRESHOLD) {
      return dateFromNumber(numberTimestamp);
    }
    // if timestamp is 0, then parsing it to long failed - let's try with String now
    if (numberTimestamp == 0) {
      return parser
          .parse(timestamp.asText())
          .get(0).getDates()
          .get(0)
          .toInstant()
          .toString();
    }
    throw new IllegalStateException();
  }

  private String dateFromNumber(final Long timestamp) {
    // if cursor value is above given threshold, then assume that it's Unix timestamp in milliseconds
    if (timestamp > MILLIS_FROM_EPOCH_THRESHOLD) {
      return Instant.ofEpochMilli(timestamp).toString();
    }
    return Instant.ofEpochSecond(timestamp).toString();
  }

  private static JsonNode getNestedNode(final JsonNode data, final List<String> fieldNames) {
    return fieldNames.stream().reduce(data, JsonNode::get, (first, second) -> second);
  }

  public Map<String, List<String>> getStreamCursorFields() {
    return streamCursorFields;
  }

}
