/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@DisplayName("KafkaRecordConsumer")
@ExtendWith(MockitoExtension.class)
public class KafkaRecordConsumerTest extends PerStreamStateMessageTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();
  private static final String TOPIC_NAME = "test.topic";
  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";

  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING))));

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private KafkaRecordConsumer consumer;

  private static final StandardNameTransformer NAMING_RESOLVER = new StandardNameTransformer();

  @BeforeEach
  public void init() {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(TOPIC_NAME));
    consumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);
  }

  @ParameterizedTest
  @ArgumentsSource(TopicMapArgumentsProvider.class)
  @SuppressWarnings("unchecked")
  public void testBuildTopicMap(final String topicPattern, final String expectedTopic) {
    final KafkaDestinationConfig config = KafkaDestinationConfig.getKafkaDestinationConfig(getConfig(topicPattern));
    consumer = new KafkaRecordConsumer(config, CATALOG, outputRecordCollector, NAMING_RESOLVER);

    final Map<AirbyteStreamNameNamespacePair, String> topicMap = consumer.buildTopicMap();
    assertEquals(1, topicMap.size());

    final AirbyteStreamNameNamespacePair streamNameNamespacePair = new AirbyteStreamNameNamespacePair(STREAM_NAME, SCHEMA_NAME);
    assertEquals(expectedTopic, topicMap.get(streamNameNamespacePair));
  }

  @Test
  @SuppressWarnings("unchecked")
  void testCannotConnectToBrokers() throws Exception {
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();

    expectedRecords.forEach(m -> assertThrows(RuntimeException.class, () -> consumer.accept(m)));

    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(SCHEMA_NAME + "." + STREAM_NAME, 0)))));
    consumer.close();
  }

  private JsonNode getConfig(final String topicPattern) {
    return getConfigWithProtocol(topicPattern, KafkaProtocol.PLAINTEXT);
  }

  private JsonNode getConfigWithProtocol(final String topicPattern, final KafkaProtocol protocol) {
    final ObjectNode protocolConfig = mapper.createObjectNode();
    protocolConfig.put("security_protocol", protocol.toString());

    switch (protocol) {
      case SASL_PLAINTEXT, SASL_SSL -> {
        protocolConfig.put("sasl_mechanism", "PLAIN");
        protocolConfig.put("sasl_jaas_config", "");
      }
      case SSL -> {
        protocolConfig.put("ssl_keystore_certificate_chain", createTestCertificate());
        protocolConfig.put("ssl_keystore_key", createTestPrivateKey());
        protocolConfig.put("ssl_truststore_certificates", createTestCACertificate());
        protocolConfig.put("ssl_endpoint_identification_algorithm", "https");
      }
    }

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", "localhost:9092")
        .put("topic_pattern", topicPattern)
        .put("sync_producer", true)
        .put("protocol", protocolConfig)
        .put("client_id", "test-client")
        .put("acks", "all")
        .put("transactional_id", "txn-id")
        .put("enable_idempotence", true)
        .put("compression_type", "none")
        .put("batch_size", "16384")
        .put("linger_ms", "0")
        .put("max_in_flight_requests_per_connection", "5")
        .put("client_dns_lookup", "use_all_dns_ips")
        .put("buffer_memory", 33554432)
        .put("max_request_size", 1048576)
        .put("retries", 1)
        .put("socket_connection_setup_timeout_ms", "10")
        .put("socket_connection_setup_timeout_max_ms", "30")
        .put("max_block_ms", "100")
        .put("request_timeout_ms", 100)
        .put("delivery_timeout_ms", 120)
        .put("send_buffer_bytes", -1)
        .put("receive_buffer_bytes", -1)
        .build());
  }

  private String createTestCertificate() {
    return """
           -----BEGIN CERTIFICATE-----
           MIICpDCCAYwCCQDU7mNqpuPZCjANBgkqhkiG9w0BAQsFADAUMRIwEAYDVQQDDAls
           b2NhbGhvc3QwHhcNMjQwMTAxMDAwMDAwWhcNMjUwMTAxMDAwMDAwWjAUMRIwEAYD
           VQQDDAlsb2NhbGhvc3QwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7
           VJTUt9Us8cKjMzEfYyjiWA4R4/M2bS1+fWIcPm15A8vGtOX5YYNvdCN2eJVuVhKY
           G8kNIV6KsPa3GU+WfSqJ0L0y4WJMzvPP4xRdLM0PbCgQ5SbN6xGLMxJ2sqCvvE0l
           XGq7JC0uyUW0h5WQyLMvQSbBBQh3/V2lKLZmMvCfVTY4DmR9iCxKLkZHZCqD0yVs
           eYAFZUhF7X8RlZCqTmXe2g8YhKpWxEk8rPVBYvN1rJjkZD6cPuD9GN1j2jRnXFP5
           Uqmb4Kj7T3YLBxZwvGqXbDcTnMMq9TqJK0vsK0xTjVGLQEKQqYvN5wRjbCXNvYLq
           H8GQKzPqvK8lBvM5nVNfAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAJh8PqLFCCqz
           b2gHBnMpBmKH8xZL2W8cK0qWcAQWC7hZJXi3kFvqm3YwIz3vLqXvW9hHnLgKOvYM
           F8HyGqCKVxMwYm8P+kqCCtqTLYDfLx3eLQvhG0QYgCKvJQ6YnPxqWDcCq6G8T9wD
           +kY3V2lVMZMQk6VrBHnT8GC+uEPxYqJXqKBmS1aCqr5X2rTH+VsJrqZDgQxUXYJ0
           j5H8Ym7W5FvYTVtqZ4LcF3OlJY5YkOCQvLnT4fLPFmvVKrQp2bMxQq2vCnN7JnPP
           DH4xC5lKVXMqLd8Pf8zVq0EWJfQYCZFTfWz4TFxYqJN2FhYb0u2BhH8yNkLQNqZD
           wUxMxQkqQqE=
           -----END CERTIFICATE-----""";
  }

  private String createTestPrivateKey() {
    return """
           -----BEGIN PRIVATE KEY-----
           MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKj
           MzEfYyjiWA4R4/M2bS1+fWIcPm15A8vGtOX5YYNvdCN2eJVuVhKYG8kNIV6KsPa3
           GU+WfSqJ0L0y4WJMzvPP4xRdLM0PbCgQ5SbN6xGLMxJ2sqCvvE0lXGq7JC0uyUW0
           h5WQyLMvQSbBBQh3/V2lKLZmMvCfVTY4DmR9iCxKLkZHZCqD0yVseYAFZUhF7X8R
           lZCqTmXe2g8YhKpWxEk8rPVBYvN1rJjkZD6cPuD9GN1j2jRnXFP5Uqmb4Kj7T3YL
           BxZwvGqXbDcTnMMq9TqJK0vsK0xTjVGLQEKQqYvN5wRjbCXNvYLqH8GQKzPqvK8l
           BvM5nVNfAgMBAAECggEAL8RP0AXWkiGCQTvFOK9bVG0AvUa1iFQ8VQNvxCvQQi5v
           VqH4HLq4Q0vBL3xFqPzFwKjYf0hqKjQqRQPW0f3YYQkJ0+Q4xMzBH7nPL0YfZX8T
           7sKPa2J1QkGMQN4YhEfkW3mX8aCXHGMXqJ0K1W7QXlVxYU6XfKjJ2TqJYCqDPQ7H
           YmF6T0L1J1sVPQY8X8GQ7K6PXqKvL8RP1L0Y4NJ8vK7LQmPQ0J0T7Q8Y4+q7L0FP
           3X1sV1QP0Y7Q8K+P7L1YvY6QXqL8PX7L1QY+P4K8L7vPQ1Y0X+P8K7Q1L+Y0P7vQ
           8X+L4K1Y7PvQ+X8K1L7Y4P+vQ8K1X7L+Y4PvQ1K8X7L+Y0PvQ1K8X7LQKBgQDmPL
           1Y7Q8K+P4vL7Q8X1L+Y4PvQ8K1X+L7Y4PvQ1K8X+L7Y0PvQ8K1X7L+Y4PvQ1K8X7
           L+Y0PvQ1K8X7L+Y4PvQ1K8X7L+Y0PvQ1K8X7L+Y4PvQ1K8X7L+Y0PvQ1K8X7L+Y4
           PvQ1K8X7L+Y0PvQ1K8X7L+Y4PvQ1K8X7L+Y0PvQwKBgQDQq9C6J7Q8K+P4vL7Q8X
           1L+Y4PvQ8K1X+L7Y4PvQ1K8X+L7Y0PvQ8K1X7L+Y4PvQ1K8X7L+Y0PvQ1K8X7L+Y
           4PvQ1K8X7L+Y0PvQ1K8X7L+Y4PvQ1K8X7L+Y0PvQ1K8X7L+Y4PvQ1K8X7L+Y0PvQ
           1K8X7L+Y4PvQ1K8X7L+Y0PvQ
           -----END PRIVATE KEY-----""";
  }

  private String createTestCACertificate() {
    return """
           -----BEGIN CERTIFICATE-----
           MIIC5TCCAc2gAwIBAgIJANTuY2qm49kKMA0GCSqGSIb3DQEBCwUAMBQxEjAQBgNV
           BAMMCWxvY2FsaG9zdDAeFw0yNDAxMDEwMDAwMDBaFw0yNTAxMDEwMDAwMDBaMBQx
           EjAQBgNVBAMMCWxvY2FsaG9zdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
           ggEBALtUlNS31SzxwqMzMR9jKOJYDhHj8zZtLX59Yhw+bXkDy8a05flhg290I3Z4
           lW5WEpgbyQ0hXoqw9rcZT5Z9KonQvTLhYkzO88/jFF0szQ9sKBDlJs3rEYszEnay
           oK+8TSVcarsken6wpAZCHXXmLayvVRUWkK4dHfmVKYuH9WUMM9lI6lYKQsH3aKQW
           c+yChKV6lqQqg9MlbHmABWVIRe1/EZWQqk5l3toPGISqVsRJPKz1QWLzdayY5GQ+
           nD7g/RjdY9o0Z1xT+VKpm+Co+092CwcWcLxql2w3E5zDKvU6iStL7CtMU41Ri0BC
           kKmLzecEY2wlzb2C6h/BkCsz6ryvJQbzOZ1TXwIDAQABo1AwTjAdBgNVHQ4EFgQU
           R2l3+mwC0pL6h3PxP5qfmT6hQ5MwHwYDVR0jBBgwFoAUR2l3+mwC0pL6h3PxP5qf
           mT6hQ5MwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAt3sQ+NLqyY7J
           q7KP1qLqY3YQvPm7+qLqv+LPvqLY+QNqLmPvqL7+PmNqLY7+qPvLmNqLPvY7+qLY
           PmNqL+v7P+qLYmNPqLv7Y+PqLNmqLv+Y7PqLmNPqLY+v7PqLNmqv+L7Y+PqLmNqv
           L7+YPqmNL+v7YPqLmNq+vL7YPqmNLv+7YPqLNmqvL+7YPqmNvL+7YPqmNLv7+YPq
           NmLv7+YqPmNv+L7Yq+PmNL+v7Yq+PmvL7Yq+PmNLv7Yq+PmvL+7Yq+PmNvL7Yq+P
           mvL+7Yq+PmNLv7Yq+PmvL7Yq+PmNLv+7Yq+PmvL7Yq+PmNLv7+Yq+PmNvL7+Yq+Pm
           vL7+Yq+PmNLv7Yq+PmvL7Yq==
           -----END CERTIFICATE-----""";
  }

  private List<AirbyteMessage> getNRecords(final int n) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(SCHEMA_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());

  }

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return consumer;
  }

  public static class TopicMapArgumentsProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(final ExtensionContext context) {
      return Stream.of(
          Arguments.of(TOPIC_NAME, "test_topic"),
          Arguments.of("test-topic", "test_topic"),
          Arguments.of("{namespace}", SCHEMA_NAME),
          Arguments.of("{stream}", STREAM_NAME),
          Arguments.of("{namespace}.{stream}." + TOPIC_NAME, "public_id_and_name_test_topic"),
          Arguments.of("{namespace}-{stream}-" + TOPIC_NAME, "public_id_and_name_test_topic"),
          Arguments.of("topic with spaces", "topic_with_spaces"));
    }

  }

}
