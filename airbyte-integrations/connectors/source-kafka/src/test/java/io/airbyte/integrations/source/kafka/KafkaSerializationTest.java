/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.confluent.kafka.schemaregistry.client.MockSchemaRegistryClient;
import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import java.util.Map;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.kafka.connect.json.JsonDeserializer;
import org.apache.kafka.connect.json.JsonSerializer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class KafkaSerializationTest {

  @ParameterizedTest
  @ValueSource(strings = {
    "io.confluent.kafka.serializers.subject.TopicNameStrategy",
    "io.confluent.kafka.serializers.subject.RecordNameStrategy",
    "io.confluent.kafka.serializers.subject.TopicRecordNameStrategy"
  })
  void avroRoundTripPreservesRecord(final String subjectNameStrategy) {
    final MockSchemaRegistryClient registry = new MockSchemaRegistryClient();
    final Map<String, Object> config = Map.of(
        "schema.registry.url", "mock://kafka-dependency-test",
        "value.subject.name.strategy", subjectNameStrategy);
    final Schema schema = new Schema.Parser().parse("""
                                                    {"type":"record","name":"Event","namespace":"test","fields":[
                                                      {"name":"message","type":"string"},
                                                      {"name":"count","type":"long"}
                                                    ]}
                                                    """);
    final GenericData.Record record = new GenericData.Record(schema);
    record.put("message", "test-event");
    record.put("count", 42L);

    try (final KafkaAvroSerializer serializer = new KafkaAvroSerializer(registry);
        final KafkaAvroDeserializer deserializer = new KafkaAvroDeserializer(registry)) {
      serializer.configure(config, false);
      deserializer.configure(config, false);
      assertEquals(record, deserializer.deserialize("events", serializer.serialize("events", record)));
    }
  }

  @Test
  void jsonRoundTripPreservesRecord() {
    final JsonNode record = Jsons.deserialize("""
                                              {"message":"test-event","count":42,"nested":{"enabled":true,"optional":null}}
                                              """);
    try (final JsonSerializer serializer = new JsonSerializer();
        final JsonDeserializer deserializer = new JsonDeserializer()) {
      assertEquals(record, deserializer.deserialize("events", serializer.serialize("events", record)));
    }
  }

}
