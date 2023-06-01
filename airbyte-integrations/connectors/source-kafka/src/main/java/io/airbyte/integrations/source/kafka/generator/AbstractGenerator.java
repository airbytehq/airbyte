package io.airbyte.integrations.source.kafka.generator;

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.kafka.converter.Converter;
import io.airbyte.integrations.source.kafka.mediator.KafkaMediator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.LinkedList;
import java.util.Queue;
import org.apache.kafka.clients.consumer.ConsumerRecord;

public class AbstractGenerator<V> implements Generator {

  private final KafkaMediator<V> mediator;
  private final Converter<V> converter;

  public AbstractGenerator(KafkaMediator<V> mediator, Converter<V> converter) {
    this.mediator = mediator;
    this.converter = converter;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read() {

    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      final Queue<ConsumerRecord<String, V>> buffer = new LinkedList<>();

      @Override
      protected AirbyteMessage computeNext() {

        // Try to load a new batch if buffer is empty
        if (buffer.isEmpty()) {
          buffer.addAll(mediator.poll());
        }

        // If it's still empty, no more data to consume
        if (buffer.isEmpty()) {
          return endOfData();
        } else {
          var message = buffer.poll();
          return converter.convertToAirbyteRecord(message.topic(), message.value());
        }
      }

    });
  }
}
