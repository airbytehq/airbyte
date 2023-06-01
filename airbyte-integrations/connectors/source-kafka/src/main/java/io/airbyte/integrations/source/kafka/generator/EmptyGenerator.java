package io.airbyte.integrations.source.kafka.generator;

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.v0.AirbyteMessage;

public class EmptyGenerator implements Generator {

  @Override
  public AutoCloseableIterator<AirbyteMessage> read() {

    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      @Override
      protected AirbyteMessage computeNext() {
        return endOfData();
      }

    });
  }
}
