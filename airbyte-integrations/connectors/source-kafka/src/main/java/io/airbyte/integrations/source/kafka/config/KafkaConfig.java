package io.airbyte.integrations.source.kafka.config;

import java.util.Map;

public record KafkaConfig(Map<String, Object> properties, Map<String, String> subscription) {

}
