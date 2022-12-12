/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.keen;

import static org.apache.kafka.clients.CommonClientConfigs.SECURITY_PROTOCOL_CONFIG;
import static org.apache.kafka.clients.producer.ProducerConfig.ACKS_CONFIG;
import static org.apache.kafka.clients.producer.ProducerConfig.BOOTSTRAP_SERVERS_CONFIG;
import static org.apache.kafka.clients.producer.ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG;
import static org.apache.kafka.clients.producer.ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG;
import static org.apache.kafka.common.config.SaslConfigs.SASL_JAAS_CONFIG;
import static org.apache.kafka.common.config.SaslConfigs.SASL_MECHANISM;
import static org.apache.kafka.common.security.auth.SecurityProtocol.SASL_SSL;
import static org.apache.kafka.common.security.plain.internals.PlainSaslServer.PLAIN_MECHANISM;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Properties;
import java.util.function.Consumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KeenDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(KeenDestination.class);
  private static final String KAFKA_BROKER = "b1.kafka-in.keen.io:9092,b2.kafka-in.keen.io:9092,b3.kafka-in.keen.io:9092";

  static final String KEEN_BASE_API_PATH = "https://api.keen.io/3.0";
  static final String CONFIG_PROJECT_ID = "project_id";
  static final String CONFIG_API_KEY = "api_key";
  static final String INFER_TIMESTAMP = "infer_timestamp";

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final String projectId = config.get(CONFIG_PROJECT_ID).textValue();
      final String apiKey = config.get(CONFIG_API_KEY).textValue();
      final KafkaProducer<String, String> producer = KafkaProducerFactory.create(projectId, apiKey);

      // throws an AuthenticationException if authentication fails
      producer.partitionsFor("ANYTHING");

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED);
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return new KeenRecordsConsumer(config, catalog, outputRecordCollector);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new KeenDestination();
    LOGGER.info("starting destination: {}", KeenDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", KeenDestination.class);
  }

  public static class KafkaProducerFactory {

    public static KafkaProducer<String, String> create(final String projectId, final String apiKey) {
      final String jaasConfig = String.format("org.apache.kafka.common.security.plain.PlainLoginModule " +
          "required username=\"%s\" password=\"%s\";", projectId, apiKey);

      final Properties props = new Properties();
      props.put(BOOTSTRAP_SERVERS_CONFIG, KAFKA_BROKER);
      props.put(SECURITY_PROTOCOL_CONFIG, SASL_SSL.name());
      props.put(SASL_MECHANISM, PLAIN_MECHANISM);
      props.put(SASL_JAAS_CONFIG, jaasConfig);
      props.put(ACKS_CONFIG, "all");
      props.put(KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
      props.put(VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
      return new KafkaProducer<>(props);
    }

  }

}
