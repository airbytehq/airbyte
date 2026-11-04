/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Iterator;
import java.util.UUID;
import java.util.function.Consumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(KafkaDestination.class);

  public static final String COLUMN_NAME_AB_ID = JavaBaseConstants.COLUMN_NAME_AB_ID;
  public static final String COLUMN_NAME_EMITTED_AT = JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
  public static final String COLUMN_NAME_DATA = JavaBaseConstants.COLUMN_NAME_DATA;
  public static final String COLUMN_NAME_STREAM = "_airbyte_stream";

  private final StandardNameTransformer namingResolver;
  private final String deploymentMode;

  public KafkaDestination() {
    this(System.getenv("DEPLOYMENT_MODE"));
  }

  KafkaDestination(final String deploymentMode) {
    this.deploymentMode = deploymentMode;
    this.namingResolver = new StandardNameTransformer();
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    final ConnectorSpecification spec = super.spec();
    if (isCloud()) {
      final ArrayNode protocols = (ArrayNode) spec.getConnectionSpecification().get("properties").get("protocol").get("oneOf");
      final Iterator<JsonNode> options = protocols.elements();
      while (options.hasNext()) {
        if (!"SASL_SSL".equals(options.next().path("properties").path("security_protocol").path("enum").path(0).asText())) {
          options.remove();
        }
      }
    }
    return spec;
  }

  private boolean isCloud() {
    return "CLOUD".equalsIgnoreCase(deploymentMode);
  }

  private void validateCloudSecurity(final JsonNode config) {
    if (isCloud() && !"SASL_SSL".equalsIgnoreCase(config.path("protocol").path("security_protocol").asText())) {
      throw new ConfigErrorException("Airbyte Cloud requires TLS for Kafka connections. Set Security Protocol to SASL_SSL.");
    }
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    validateCloudSecurity(config);
    try {
      final String testTopic = config.has("test_topic") ? config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        final KafkaDestinationConfig kafkaDestinationConfig = KafkaDestinationConfig.getKafkaDestinationConfig(config);
        final KafkaProducer<String, JsonNode> producer = kafkaDestinationConfig.getProducer();
        final String key = UUID.randomUUID().toString();
        final JsonNode value = Jsons.jsonNode(ImmutableMap.of(
            COLUMN_NAME_AB_ID, key,
            COLUMN_NAME_STREAM, "test-topic-stream",
            COLUMN_NAME_EMITTED_AT, System.currentTimeMillis(),
            COLUMN_NAME_DATA, Jsons.jsonNode(ImmutableMap.of("test-key", "test-value"))));

        final RecordMetadata metadata = producer.send(new ProducerRecord<>(
            namingResolver.getIdentifier(testTopic), key, value)).get();
        producer.flush();

        LOGGER.info("Successfully connected to Kafka brokers for topic '{}'.", metadata.topic());
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to connect to the Kafka brokers: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect to the Kafka brokers with provided configuration. \n" + e.getMessage());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    validateCloudSecurity(config);
    return new KafkaRecordConsumer(KafkaDestinationConfig.getKafkaDestinationConfig(config),
        catalog,
        outputRecordCollector,
        namingResolver);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new KafkaDestination();
    LOGGER.info("Starting destination: {}", KafkaDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("Completed destination: {}", KafkaDestination.class);
  }

}
