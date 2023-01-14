/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.List;

public interface KafkaFormat {

  boolean isAccessible();

  List<AirbyteStream> getStreams();

  AutoCloseableIterator<AirbyteMessage> read();

}
