/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.connect.json.JsonDeserializer;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.utility.DockerImageName;

public class KafkaDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();
  private static final String TOPIC_NAME = "test.topic";

  private static KafkaContainer KAFKA;

  private final NamingConventionTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-kafka:dev";
  }

  @Override
  protected JsonNode getConfig() {
    final ObjectNode stubProtocolConfig = mapper.createObjectNode();
    stubProtocolConfig.put("security_protocol", KafkaProtocol.PLAINTEXT.toString());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", KAFKA.getBootstrapServers())
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("sync_producer", true)
        .put("protocol", stubProtocolConfig)
        .put("client_id", "test-client")
        .put("acks", "all")
        .put("enable_idempotence", true)
        .put("compression_type", "none")
        .put("batch_size", 16384)
        .put("linger_ms", "0")
        .put("max_in_flight_requests_per_connection", 5)
        .put("client_dns_lookup", "use_all_dns_ips")
        .put("buffer_memory", "33554432")
        .put("max_request_size", 1048576)
        .put("retries", 2147483647)
        .put("socket_connection_setup_timeout_ms", "10000")
        .put("socket_connection_setup_timeout_max_ms", "30000")
        .put("max_block_ms", "60000")
        .put("request_timeout_ms", 30000)
        .put("delivery_timeout_ms", 120000)
        .put("send_buffer_bytes", -1)
        .put("receive_buffer_bytes", -1)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final ObjectNode stubProtocolConfig = mapper.createObjectNode();
    stubProtocolConfig.put("security_protocol", KafkaProtocol.SASL_PLAINTEXT.toString());
    stubProtocolConfig.put("sasl_mechanism", "PLAIN");
    stubProtocolConfig.put("sasl_jaas_config", "invalid");

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", KAFKA.getBootstrapServers())
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("test_topic", "check-topic")
        .put("protocol", stubProtocolConfig)
        .put("client_id", "test-client")
        .put("acks", "all")
        .put("enable_idempotence", true)
        .put("compression_type", "none")
        .put("batch_size", 16384)
        .put("linger_ms", 0)
        .put("max_in_flight_requests_per_connection", 5)
        .put("client_dns_lookup", "use_all_dns_ips")
        .put("buffer_memory", 33554432)
        .put("max_request_size", 1048576)
        .put("retries", 2147483647)
        .put("socket_connection_setup_timeout_ms", 10000)
        .put("socket_connection_setup_timeout_max_ms", 30000)
        .put("max_block_ms", 60000)
        .put("request_timeout_ms", 30000)
        .put("delivery_timeout_ms", 120000)
        .put("send_buffer_bytes", -1)
        .put("receive_buffer_bytes", -1)
        .build());
  }

  /**
   * Creates a configuration with SSL protocol for testing SSL certificate authentication. Note: This
   * config will fail connection check because KAFKA testcontainer doesn't have SSL enabled, but it's
   * useful for verifying SSL configuration parsing and initialization.
   */
  protected JsonNode getSslConfig() {
    final ObjectNode sslProtocolConfig = mapper.createObjectNode();
    sslProtocolConfig.put("security_protocol", KafkaProtocol.SSL.toString());
    sslProtocolConfig.put("ssl_keystore_certificate_chain", getTestCertificate());
    sslProtocolConfig.put("ssl_keystore_key", getTestPrivateKey());
    sslProtocolConfig.put("ssl_truststore_certificates", getTestCACertificate());
    sslProtocolConfig.put("ssl_endpoint_identification_algorithm", "https");

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", KAFKA.getBootstrapServers())
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("test_topic", "ssl-check-topic")
        .put("protocol", sslProtocolConfig)
        .put("client_id", "test-ssl-client")
        .put("acks", "all")
        .put("enable_idempotence", true)
        .put("compression_type", "none")
        .put("batch_size", 16384)
        .put("linger_ms", "0")
        .put("max_in_flight_requests_per_connection", 5)
        .put("client_dns_lookup", "use_all_dns_ips")
        .put("buffer_memory", "33554432")
        .put("max_request_size", 1048576)
        .put("retries", 2147483647)
        .put("socket_connection_setup_timeout_ms", "10000")
        .put("socket_connection_setup_timeout_max_ms", "30000")
        .put("max_block_ms", "60000")
        .put("request_timeout_ms", 30000)
        .put("delivery_timeout_ms", 120000)
        .put("send_buffer_bytes", -1)
        .put("receive_buffer_bytes", -1)
        .build());
  }

  private String getTestCertificate() {
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

  private String getTestPrivateKey() {
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

  private String getTestCACertificate() {
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

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return "";
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace) {
    return retrieveRecords(testEnv, streamName, namespace, null);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final Map<String, Object> props = ImmutableMap.<String, Object>builder()
        .put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, KAFKA.getBootstrapServers())
        .put(ConsumerConfig.GROUP_ID_CONFIG, namingResolver.getIdentifier(namespace + "-" + streamName))
        .put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest")
        .put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName())
        .put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class.getName())
        .build();
    final KafkaConsumer<String, JsonNode> consumer = new KafkaConsumer<>(props);
    final List<JsonNode> records = new ArrayList<>();
    final String topic = namingResolver.getIdentifier(namespace + "." + streamName + "." + TOPIC_NAME);

    consumer.subscribe(Collections.singletonList(topic));
    consumer.poll(Duration.ofMillis(20000L)).iterator()
        .forEachRemaining(record -> records.add(record.value().get(JavaBaseConstants.COLUMN_NAME_DATA)));
    consumer.close();

    return records;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    KAFKA = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:6.2.0"));
    KAFKA.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    KAFKA.close();
  }

}
