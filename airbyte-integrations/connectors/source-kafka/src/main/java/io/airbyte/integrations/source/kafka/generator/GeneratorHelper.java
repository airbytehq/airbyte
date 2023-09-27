/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.generator;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.kafka.config.SourceConfig;
import io.airbyte.integrations.source.kafka.converter.AvroConverter;
import io.airbyte.integrations.source.kafka.converter.Converter;
import io.airbyte.integrations.source.kafka.converter.JsonConverter;
import io.airbyte.integrations.source.kafka.mediator.DefaultKafkaMediator;
import io.airbyte.integrations.source.kafka.mediator.KafkaMediator;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.avro.generic.GenericRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;

public class GeneratorHelper {

  public static Generator buildFrom(SourceConfig config, Map<TopicPartition, Long> initialOffsets) {
    return switch (config.format()) {
      case AVRO -> {
        final KafkaConsumer<String, GenericRecord> consumer = new KafkaConsumer<>(config.kafkaConfig().properties());
        final Converter<GenericRecord> converter = new AvroConverter();
        final KafkaMediator mediator = new DefaultKafkaMediator<>(consumer, converter, config.pollingTimeInMs(),
            config.kafkaConfig().subscription(),
            initialOffsets);

        yield Generator.Builder.newInstance()
            .withMaxRecords(config.maxRecords())
            .withMaxRetries(config.maxRetries())
            .withMediator(mediator).build();
      }
      case JSON -> {
        final KafkaConsumer<String, JsonNode> consumer = new KafkaConsumer<>(config.kafkaConfig().properties());
        final Converter<JsonNode> converter = new JsonConverter();
        final KafkaMediator mediator = new DefaultKafkaMediator<>(consumer, converter, config.pollingTimeInMs(),
            config.kafkaConfig().subscription(),
            initialOffsets);

        yield Generator.Builder.newInstance()
            .withMaxRecords(config.maxRecords())
            .withMaxRetries(config.maxRetries())
            .withMediator(mediator)
            .build();
      }
    };
  }

}
