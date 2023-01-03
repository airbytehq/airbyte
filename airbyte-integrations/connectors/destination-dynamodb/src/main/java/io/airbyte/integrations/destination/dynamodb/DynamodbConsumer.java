/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.*;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DynamodbConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(DynamodbConsumer.class);

  private final DynamodbDestinationConfig dynamodbDestinationConfig;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, DynamodbWriter> streamNameAndNamespaceToWriters;

  public DynamodbConsumer(final DynamodbDestinationConfig dynamodbDestinationConfig,
                          final ConfiguredAirbyteCatalog configuredCatalog,
                          final Consumer<AirbyteMessage> outputRecordCollector) {
    this.dynamodbDestinationConfig = dynamodbDestinationConfig;
    this.configuredCatalog = configuredCatalog;
    this.outputRecordCollector = outputRecordCollector;
    this.streamNameAndNamespaceToWriters = new HashMap<>(configuredCatalog.getStreams().size());
  }

  @Override
  protected void startTracked() throws Exception {

    final var endpoint = dynamodbDestinationConfig.getEndpoint();
    final AWSCredentials awsCreds =
        new BasicAWSCredentials(dynamodbDestinationConfig.getAccessKeyId(), dynamodbDestinationConfig.getSecretAccessKey());
    AmazonDynamoDB amazonDynamodb = null;

    if (endpoint.isEmpty()) {
      amazonDynamodb = AmazonDynamoDBClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(dynamodbDestinationConfig.getRegion())
          .build();
    } else {
      final ClientConfiguration clientConfiguration = new ClientConfiguration();
      clientConfiguration.setSignerOverride("AWSDynamodbSignerType");

      amazonDynamodb = AmazonDynamoDBClientBuilder
          .standard()
          .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, dynamodbDestinationConfig.getRegion()))
          .withClientConfiguration(clientConfiguration)
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .build();
    }

    final var uploadTimestamp = System.currentTimeMillis();

    for (final ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      final var writer = new DynamodbWriter(dynamodbDestinationConfig, amazonDynamodb, configuredStream, uploadTimestamp);

      final AirbyteStream stream = configuredStream.getStream();
      final AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair
          .fromAirbyteStream(stream);
      streamNameAndNamespaceToWriters.put(streamNamePair, writer);
    }
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) throws Exception {
    if (airbyteMessage.getType() == AirbyteMessage.Type.STATE) {
      outputRecordCollector.accept(airbyteMessage);
      return;
    } else if (airbyteMessage.getType() != AirbyteMessage.Type.RECORD) {
      return;
    }

    final AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
    final AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair
        .fromRecordMessage(recordMessage);

    if (!streamNameAndNamespaceToWriters.containsKey(pair)) {
      throw new IllegalArgumentException(
          String.format(
              "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(configuredCatalog), Jsons.serialize(recordMessage)));
    }

    streamNameAndNamespaceToWriters.get(pair).write(UUID.randomUUID(), recordMessage);
  }

  @Override
  protected void close(final boolean hasFailed) throws Exception {
    for (final DynamodbWriter handler : streamNameAndNamespaceToWriters.values()) {
      handler.close(hasFailed);
    }
  }

}
