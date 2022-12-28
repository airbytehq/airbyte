/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.protocol.objects.AirbyteMessage;
import io.airbyte.commons.protocol.objects.AirbyteMessageType;
import io.airbyte.commons.protocol.objects.ConnectorSpecification;
import io.airbyte.commons.protocol.objects.impl.AirbyteMessageAdapter;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class AirbyteMessageReader {

  final Map<AirbyteMessageType, List<AirbyteMessage>> sortedMessages;

  public AirbyteMessageReader(final Stream<io.airbyte.protocol.models.AirbyteMessage> airbyteMessageStream) {
    sortedMessages = sortMessages(airbyteMessageStream);
  }

  public Stream<ConnectorSpecification> getSpecs() {
    return getMessagesByType(AirbyteMessageType.SPEC, AirbyteMessage::getSpec);
  }

  public Stream<AirbyteTraceMessage> getTraces() {
    return getMessagesByType(AirbyteMessageType.TRACE, AirbyteMessage::getTrace);
  }

  private <T> Stream<T> getMessagesByType(final AirbyteMessageType key, final Function<AirbyteMessage, T> mapper) {
    return sortedMessages.getOrDefault(key, List.of()).stream().map(mapper);
  }

  private static Map<AirbyteMessageType, List<AirbyteMessage>> sortMessages(final Stream<io.airbyte.protocol.models.AirbyteMessage> messages) {
    return messages.map(AirbyteMessageAdapter::new).collect(Collectors.groupingBy(AirbyteMessage::getType));
  }

}
