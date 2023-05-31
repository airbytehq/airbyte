/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.time.Instant;
import java.util.List;

public class ElasticsearchUtils {

  public static AutoCloseableIterator<JsonNode> getDataIterator(final ElasticsearchConnection connection,
                                                                final AirbyteStream stream) {
    final AirbyteStreamNameNamespacePair airbyteStream = AirbyteStreamUtils.convertFromAirbyteStream(stream);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        List<JsonNode> data = connection.getRecords(stream.getName());
        return AutoCloseableIterators.fromIterator(data.iterator(), airbyteStream);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  public static AutoCloseableIterator<AirbyteMessage> getMessageIterator(final AutoCloseableIterator<JsonNode> recordIterator,
                                                                         final String streamName,
                                                                         final String streamNamespace) {
    return AutoCloseableIterators.transform(recordIterator,
        AirbyteStreamUtils.convertFromNameAndNamespace(streamName, streamNamespace),
        r -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(streamName)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(r)));
  }

}
