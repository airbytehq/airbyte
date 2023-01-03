/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.UUID;
import java.util.function.Consumer;
import org.apache.pulsar.client.api.MessageId;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.schema.GenericRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PulsarDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PulsarDestination.class);

  public static final String COLUMN_NAME_AB_ID = JavaBaseConstants.COLUMN_NAME_AB_ID;
  public static final String COLUMN_NAME_EMITTED_AT = JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
  public static final String COLUMN_NAME_DATA = JavaBaseConstants.COLUMN_NAME_DATA;
  public static final String COLUMN_NAME_STREAM = "_airbyte_stream";

  private final StandardNameTransformer namingResolver;

  public PulsarDestination() {
    this.namingResolver = new StandardNameTransformer();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final PulsarDestinationConfig pulsarConfig = PulsarDestinationConfig.getPulsarDestinationConfig(config);
      final String testTopic = pulsarConfig.getTestTopic();
      if (!testTopic.isBlank()) {
        final String key = UUID.randomUUID().toString();
        final GenericRecord value = Schema.generic(PulsarDestinationConfig.getSchemaInfo())
            .newRecordBuilder()
            .set(PulsarDestination.COLUMN_NAME_AB_ID, key)
            .set(PulsarDestination.COLUMN_NAME_STREAM, "test-topic-stream")
            .set(PulsarDestination.COLUMN_NAME_EMITTED_AT, System.currentTimeMillis())
            .set(PulsarDestination.COLUMN_NAME_DATA, Jsons.jsonNode(ImmutableMap.of("test-key", "test-value")))
            .build();

        try (final PulsarClient client = PulsarUtils.buildClient(pulsarConfig.getServiceUrl());
            final Producer<GenericRecord> producer = PulsarUtils.buildProducer(client, Schema.generic(PulsarDestinationConfig.getSchemaInfo()),
                pulsarConfig.getProducerConfig(), pulsarConfig.uriForTopic(testTopic))) {
          final MessageId messageId = producer.send(value);

          producer.flush();

          LOGGER.info("Successfully sent message id '{}' to Pulsar brokers for topic '{}'.", messageId, testTopic);
        }
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to connect to the Pulsar brokers: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect to the Pulsar brokers with provided configuration. \n" + e.getMessage());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final PulsarDestinationConfig pulsarConfig = PulsarDestinationConfig.getPulsarDestinationConfig(config);
    return new PulsarRecordConsumer(pulsarConfig,
        catalog,
        PulsarUtils.buildClient(pulsarConfig.getServiceUrl()),
        outputRecordCollector,
        namingResolver);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new PulsarDestination();
    LOGGER.info("Starting destination: {}", PulsarDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("Completed destination: {}", PulsarDestination.class);
  }

}
