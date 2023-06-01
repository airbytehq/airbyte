package io.airbyte.integrations.source.kafka;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.kafka.consumer.ConsumerManager;
import io.airbyte.integrations.source.kafka.converter.AvroConverter;
import io.airbyte.integrations.source.kafka.converter.Converter;
import io.airbyte.integrations.source.kafka.generator.AvroGenerator;
import io.airbyte.integrations.source.kafka.generator.Generator;
import io.airbyte.integrations.source.kafka.mediator.KafkaMediator;
import io.airbyte.integrations.source.kafka.mediator.SimpleKafkaMediator;
import org.apache.avro.generic.GenericRecord;
import org.apache.commons.lang3.NotImplementedException;
import org.apache.commons.lang3.tuple.Triple;
import org.apache.kafka.clients.consumer.KafkaConsumer;


public class KafkaDependenciesInitializer {

    public static Triple<KafkaMediator<?>, Converter<?>,Generator> getDependencies(JsonNode config, String eventType) {

        // this will change based on the value will be passed from the KafkaSource config
        return switch (eventType) {
            case "AVRO" -> {
                KafkaConsumer<String, GenericRecord> consumer = ConsumerManager.getAvroConsumer(config);
                KafkaMediator<GenericRecord> mediator = new SimpleKafkaMediator<>(consumer);
                AvroConverter converter = new AvroConverter();
                Generator generator = new AvroGenerator(mediator, converter);

                yield Triple.of(mediator, converter, generator);
            }
            default -> throw new NotImplementedException("JsonGenerator not yet implemented");

        };

    }


}
