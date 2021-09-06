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

package io.airbyte.integrations.destination.dynamodb;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.*;
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

  private AirbyteMessage lastStateMessage = null;

  public DynamodbConsumer(DynamodbDestinationConfig dynamodbDestinationConfig,
                          ConfiguredAirbyteCatalog configuredCatalog,
                          Consumer<AirbyteMessage> outputRecordCollector) {
    this.dynamodbDestinationConfig = dynamodbDestinationConfig;
    this.configuredCatalog = configuredCatalog;
    this.outputRecordCollector = outputRecordCollector;
    this.streamNameAndNamespaceToWriters = new HashMap<>(configuredCatalog.getStreams().size());
  }

  @Override
  protected void startTracked() throws Exception {

    var endpoint = dynamodbDestinationConfig.getEndpoint();
    AWSCredentials awsCreds = new BasicAWSCredentials(dynamodbDestinationConfig.getAccessKeyId(), dynamodbDestinationConfig.getSecretAccessKey());
    AmazonDynamoDB amazonDynamodb = null;

    if (endpoint.isEmpty()) {
      amazonDynamodb = AmazonDynamoDBClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(dynamodbDestinationConfig.getRegion())
          .build();
    } else {
      ClientConfiguration clientConfiguration = new ClientConfiguration();
      clientConfiguration.setSignerOverride("AWSDynamodbSignerType");

      amazonDynamodb = AmazonDynamoDBClientBuilder
          .standard()
          .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, dynamodbDestinationConfig.getRegion()))
          .withClientConfiguration(clientConfiguration)
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .build();
    }

    var uploadTimestamp = System.currentTimeMillis();

    for (ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      var writer = new DynamodbWriter(dynamodbDestinationConfig, amazonDynamodb, configuredStream, uploadTimestamp);

      AirbyteStream stream = configuredStream.getStream();
      AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair
          .fromAirbyteSteam(stream);
      streamNameAndNamespaceToWriters.put(streamNamePair, writer);
    }
  }

  @Override
  protected void acceptTracked(AirbyteMessage airbyteMessage) throws Exception {
    if (airbyteMessage.getType() == AirbyteMessage.Type.STATE) {
      this.lastStateMessage = airbyteMessage;
      return;
    } else if (airbyteMessage.getType() != AirbyteMessage.Type.RECORD) {
      return;
    }

    AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
    AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair
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
  protected void close(boolean hasFailed) throws Exception {
    for (DynamodbWriter handler : streamNameAndNamespaceToWriters.values()) {
      handler.close(hasFailed);
    }
    // DynamoDB stream uploader is all or nothing if a failure happens in the destination.
    if (!hasFailed) {
      outputRecordCollector.accept(lastStateMessage);
    }
  }

}
