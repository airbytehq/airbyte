package io.airbyte.integrations.source.kafka.mediator;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.kafka.KafkaProtocol;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.config.SaslConfigs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SimpleKafkaMediator<V> implements KafkaMediator<V> {

    private KafkaConsumer<String, V> consumer;

    public SimpleKafkaMediator(KafkaConsumer<String, V> consumer) {
        this.consumer = consumer;
    }

    @Override
    public List<ConsumerRecord<String, V>> poll() {
        List<ConsumerRecord<String, V>> output = new ArrayList<>();
        consumer.poll(Duration.of(5000L, ChronoUnit.MILLIS)).forEach(record -> output.add(record));
        return output;
    }

}
