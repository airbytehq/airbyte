package io.airbyte.integrations.source.kafka.mediator;

import java.util.List;
import org.apache.kafka.clients.consumer.ConsumerRecord;

public interface KafkaMediator<V> {

  List<ConsumerRecord<String, V>> poll();

}
