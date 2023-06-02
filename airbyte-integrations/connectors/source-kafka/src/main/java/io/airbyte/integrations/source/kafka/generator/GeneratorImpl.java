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

public class GeneratorImpl<V> implements Generator {

  private final KafkaMediator<V> mediator;
  private final Converter<V> converter;
  private final int maxRecords;


  public GeneratorImpl(KafkaMediator<V> mediator, Converter<V> converter, int maxRecords) {
    this.mediator = mediator;
    this.converter = converter;
    this.maxRecords = maxRecords;
  }

  @Override
  final public AutoCloseableIterator<AirbyteMessage> read() {

    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      private int totalEmitted = 0;

      final Queue<ConsumerRecord<String, V>> buffer = new LinkedList<>();

      @Override
      protected AirbyteMessage computeNext() {

        // Try to load a new batch if buffer is empty
        if (buffer.isEmpty()) {
          // Only load a new batch if we haven't reached max_records
          if (this.totalEmitted < GeneratorImpl.this.maxRecords) {
            var batch = mediator.poll();
            totalEmitted += batch.size();
            buffer.addAll(mediator.poll());
          } else {
            return endOfData();
          }
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
