/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermission;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.config.SaslConfigs;
import org.apache.kafka.common.config.SslConfigs;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.connect.json.JsonSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaDestinationConfig {

  protected static final Logger LOGGER = LoggerFactory.getLogger(KafkaDestinationConfig.class);

  private final String topicPattern;
  private final boolean sync;
  private final KafkaProducer<String, JsonNode> producer;
  private final List<File> temporarySslFiles;

  private final Thread shutdownHook;

  private KafkaDestinationConfig(final String topicPattern, final boolean sync, final JsonNode config) {
    this.topicPattern = topicPattern;
    this.sync = sync;
    this.temporarySslFiles = new ArrayList<>();
    this.producer = buildKafkaProducer(config);

    this.shutdownHook = new Thread(this::cleanupTemporaryFiles);
    Runtime.getRuntime().addShutdownHook(shutdownHook);
  }

  public static KafkaDestinationConfig getKafkaDestinationConfig(final JsonNode config) {
    return new KafkaDestinationConfig(
        config.get("topic_pattern").asText(),
        config.has("sync_producer") && config.get("sync_producer").asBoolean(),
        config);
  }

  private KafkaProducer<String, JsonNode> buildKafkaProducer(final JsonNode config) {
    final Map<String, Object> props = ImmutableMap.<String, Object>builder()
        .put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, config.get("bootstrap_servers").asText())
        .putAll(propertiesByProtocol(config))
        .put(ProducerConfig.CLIENT_ID_CONFIG,
            config.has("client_id") ? config.get("client_id").asText() : "")
        .put(ProducerConfig.ACKS_CONFIG, config.get("acks").asText())
        .put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, config.get("enable_idempotence").asBoolean())
        .put(ProducerConfig.COMPRESSION_TYPE_CONFIG, config.get("compression_type").asText())
        .put(ProducerConfig.BATCH_SIZE_CONFIG, config.get("batch_size").asInt())
        .put(ProducerConfig.LINGER_MS_CONFIG, config.get("linger_ms").asLong())
        .put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION,
            config.get("max_in_flight_requests_per_connection").asInt())
        .put(ProducerConfig.CLIENT_DNS_LOOKUP_CONFIG, config.get("client_dns_lookup").asText())
        .put(ProducerConfig.BUFFER_MEMORY_CONFIG, config.get("buffer_memory").asLong())
        .put(ProducerConfig.MAX_REQUEST_SIZE_CONFIG, config.get("max_request_size").asInt())
        .put(ProducerConfig.RETRIES_CONFIG, config.get("retries").asInt())
        .put(ProducerConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MS_CONFIG,
            config.get("socket_connection_setup_timeout_ms").asLong())
        .put(ProducerConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MAX_MS_CONFIG,
            config.get("socket_connection_setup_timeout_max_ms").asLong())
        .put(ProducerConfig.MAX_BLOCK_MS_CONFIG, config.get("max_block_ms").asInt())
        .put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, config.get("request_timeout_ms").asInt())
        .put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, config.get("delivery_timeout_ms").asInt())
        .put(ProducerConfig.SEND_BUFFER_CONFIG, config.get("send_buffer_bytes").asInt())
        .put(ProducerConfig.RECEIVE_BUFFER_CONFIG, config.get("receive_buffer_bytes").asInt())
        .put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName())
        .put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class.getName())
        .build();

    final Map<String, Object> filteredProps = props.entrySet().stream()
        .filter(entry -> entry.getValue() != null && !entry.getValue().toString().isBlank())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

    return new KafkaProducer<>(filteredProps);
  }

  private Map<String, Object> propertiesByProtocol(final JsonNode config) {
    final JsonNode protocolConfig = config.get("protocol");
    final KafkaProtocol protocol = KafkaProtocol.valueOf(protocolConfig.get("security_protocol").asText().toUpperCase());
    LOGGER.info("Configuring Kafka with security protocol: {}", protocol);
    final ImmutableMap.Builder<String, Object> builder = ImmutableMap.<String, Object>builder()
        .put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, protocol.toString());

    switch (protocol) {
      case PLAINTEXT -> {}
      case SASL_SSL, SASL_PLAINTEXT -> {
        builder.put(SaslConfigs.SASL_JAAS_CONFIG, protocolConfig.get("sasl_jaas_config").asText());
        builder.put(SaslConfigs.SASL_MECHANISM, protocolConfig.get("sasl_mechanism").asText());
      }
      case SSL -> {
        try {
          configureSslProperties(builder, protocolConfig);
        } catch (IOException e) {
          throw new RuntimeException("Failed to configure SSL properties", e);
        }
      }
      default -> throw new RuntimeException("Unexpected Kafka protocol: " + Jsons.serialize(protocol));
    }

    return builder.build();
  }

  /**
   * Configures SSL properties for Kafka producer using PEM-format certificates.
   * Creates temporary files for certificates and keys as Kafka requires file paths.
   */
  private void configureSslProperties(final ImmutableMap.Builder<String, Object> builder, final JsonNode protocolConfig) throws IOException {
    LOGGER.info("Configuring SSL certificate authentication");

    if (protocolConfig.has("ssl_keystore_certificate_chain") && !protocolConfig.get("ssl_keystore_certificate_chain").asText().isBlank()) {
      final String certChain = protocolConfig.get("ssl_keystore_certificate_chain").asText();
      final String privateKey = protocolConfig.get("ssl_keystore_key").asText();
      final String keystorePassword = protocolConfig.has("ssl_keystore_password")
          ? protocolConfig.get("ssl_keystore_password").asText()
          : "";

      final String combinedPem = certChain + "\n" + privateKey;
      final File keystoreFile = writeToTempFile(combinedPem, "kafka-keystore", ".pem");

      builder.put(SslConfigs.SSL_KEYSTORE_LOCATION_CONFIG, keystoreFile.getAbsolutePath());
      builder.put(SslConfigs.SSL_KEYSTORE_TYPE_CONFIG, "PEM");
      LOGGER.info("SSL keystore configured with combined certificate and key at: {}", keystoreFile.getAbsolutePath());

      if (!keystorePassword.isBlank()) {
        builder.put(SslConfigs.SSL_KEY_PASSWORD_CONFIG, keystorePassword);
      }
    }

    if (protocolConfig.has("ssl_truststore_certificates") && !protocolConfig.get("ssl_truststore_certificates").asText().isBlank()) {
      final String caCerts = protocolConfig.get("ssl_truststore_certificates").asText();
      final String truststorePassword = protocolConfig.has("ssl_truststore_password")
          ? protocolConfig.get("ssl_truststore_password").asText()
          : "";

      final File trustFile = writeToTempFile(caCerts, "kafka-truststore", ".pem");
      builder.put(SslConfigs.SSL_TRUSTSTORE_LOCATION_CONFIG, trustFile.getAbsolutePath());
      builder.put(SslConfigs.SSL_TRUSTSTORE_TYPE_CONFIG, "PEM");
      LOGGER.info("SSL truststore configured at: {}", trustFile.getAbsolutePath());

      if (!truststorePassword.isBlank()) {
        builder.put(SslConfigs.SSL_TRUSTSTORE_PASSWORD_CONFIG, truststorePassword);
      }
    }

    if (protocolConfig.has("ssl_endpoint_identification_algorithm")) {
      final String endpointAlgorithm = protocolConfig.get("ssl_endpoint_identification_algorithm").asText();
      builder.put(SslConfigs.SSL_ENDPOINT_IDENTIFICATION_ALGORITHM_CONFIG, endpointAlgorithm);
      LOGGER.info("SSL endpoint identification algorithm set to: {}", endpointAlgorithm.isBlank() ? "disabled" : endpointAlgorithm);
    }
  }

  /**
   * Writes content to a temporary file with restricted permissions.
   * The file is marked for deletion on JVM exit and tracked for cleanup.
   */
  private File writeToTempFile(final String content, final String prefix, final String suffix) throws IOException {
    final Set<PosixFilePermission> permissions = PosixFilePermissions.fromString("rw-------");
    Path tempFile;

    try {
      tempFile = Files.createTempFile(prefix, suffix, PosixFilePermissions.asFileAttribute(permissions));
    } catch (UnsupportedOperationException e) {
      tempFile = Files.createTempFile(prefix, suffix);
      LOGGER.warn("POSIX file permissions not supported, temporary file created without restricted permissions");
    }

    Files.writeString(tempFile, content, StandardCharsets.UTF_8);

    final File file = tempFile.toFile();
    file.deleteOnExit();

    temporarySslFiles.add(file);

    LOGGER.debug("Created temporary SSL file: {}", file.getAbsolutePath());
    return file;
  }

  /**
   * Cleans up all temporary SSL files created during configuration.
   * Called automatically by shutdown hook or can be called manually.
   */
  private void cleanupTemporaryFiles() {
    LOGGER.debug("Cleaning up {} temporary SSL files", temporarySslFiles.size());
    for (File file : temporarySslFiles) {
      try {
        if (file.exists() && file.delete()) {
          LOGGER.debug("Deleted temporary SSL file: {}", file.getAbsolutePath());
        }
      } catch (Exception e) {
        LOGGER.warn("Failed to delete temporary SSL file: {}", file.getAbsolutePath(), e);
      }
    }
    temporarySslFiles.clear();
  }

  /**
   * Closes the producer and cleans up resources.
   * Should be called when the config is no longer needed.
   */
  public void close() {
    try {
      if (producer != null) {
        producer.close();
      }
    } finally {
      cleanupTemporaryFiles();
      try {
        Runtime.getRuntime().removeShutdownHook(shutdownHook);
      } catch (IllegalStateException e) {
        // Ignore if shutdown is already in progress
      }
    }
  }

  public String getTopicPattern() {
    return topicPattern;
  }

  public boolean isSync() {
    return sync;
  }

  public KafkaProducer<String, JsonNode> getProducer() {
    return producer;
  }

}
