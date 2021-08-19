/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
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
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      final String projectId = config.get(CONFIG_PROJECT_ID).textValue();
      final String apiKey = config.get(CONFIG_API_KEY).textValue();
      KafkaProducer<String, String> producer = KafkaProducerFactory.create(projectId, apiKey);

      // throws an AuthenticationException if authentication fails
      producer.partitionsFor("ANYTHING");

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED);
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return new KeenRecordsConsumer(config, catalog, outputRecordCollector);
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new KeenDestination();
    LOGGER.info("starting destination: {}", KeenDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", KeenDestination.class);
  }

  public static class KafkaProducerFactory {

    public static KafkaProducer<String, String> create(String projectId, String apiKey) {
      String jaasConfig = String.format("org.apache.kafka.common.security.plain.PlainLoginModule " +
          "required username=\"%s\" password=\"%s\";", projectId, apiKey);

      Properties props = new Properties();
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
