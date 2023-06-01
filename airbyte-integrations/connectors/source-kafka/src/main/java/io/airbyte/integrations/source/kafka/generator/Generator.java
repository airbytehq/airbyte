package io.airbyte.integrations.source.kafka.generator;

import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;

public interface Generator {

  AutoCloseableIterator<AirbyteMessage> read();
}

