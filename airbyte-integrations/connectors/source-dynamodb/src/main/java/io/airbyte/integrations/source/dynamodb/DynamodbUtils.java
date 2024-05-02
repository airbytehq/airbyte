/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.configoss.StateWrapper;
import io.airbyte.configoss.helpers.StateMessageHelper;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

public class DynamodbUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(DynamodbUtils.class);

  private DynamodbUtils() {

  }

  public static DynamoDbClient createDynamoDbClient(final DynamodbConfig dynamodbConfig) {
    final var dynamoDbClientBuilder = DynamoDbClient.builder();
    AwsCredentialsProvider awsCredentialsProvider;
    if (!StringUtils.isBlank(dynamodbConfig.accessKey()) && !StringUtils.isBlank(dynamodbConfig.secretKey())) {
      LOGGER.info("Creating credentials using access key and secret key");
      AwsCredentials awsCreds = AwsBasicCredentials.create(dynamodbConfig.accessKey(), dynamodbConfig.secretKey());
      awsCredentialsProvider = StaticCredentialsProvider.create(awsCreds);
    } else {
      LOGGER.info("Using Role Based Access");
      awsCredentialsProvider = DefaultCredentialsProvider.create();
    }

    // configure access credentials
    dynamoDbClientBuilder.credentialsProvider(awsCredentialsProvider);

    if (dynamodbConfig.region() != null) {
      dynamoDbClientBuilder.region(dynamodbConfig.region());
    }

    if (dynamodbConfig.endpoint() != null) {
      dynamoDbClientBuilder.endpointOverride(dynamodbConfig.endpoint());
    }

    return dynamoDbClientBuilder.build();
  }

  public static AirbyteMessage mapAirbyteMessage(final String stream, final JsonNode data) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(stream)
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(data));
  }

  public static StreamState deserializeStreamState(final JsonNode state) {
    final Optional<StateWrapper> typedState =
        StateMessageHelper.getTypedState(state);
    return typedState.map(stateWrapper -> switch (stateWrapper.getStateType()) {
      case STREAM:
        yield new StreamState(AirbyteStateMessage.AirbyteStateType.STREAM,
            stateWrapper.getStateMessages().stream().map(DynamodbUtils::convertStateMessage).toList());
      case LEGACY:
        yield new StreamState(AirbyteStateMessage.AirbyteStateType.LEGACY, List.of(
            new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(stateWrapper.getLegacyState())));
      case GLOBAL:
        throw new UnsupportedOperationException("Unsupported stream state");
    }).orElseGet(() -> {
      // create empty initial state
      return new StreamState(AirbyteStateMessage.AirbyteStateType.STREAM, List.of(
          new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.STREAM)
              .withStream(new AirbyteStreamState())));

    });
  }

  private static AirbyteStateMessage convertStateMessage(final io.airbyte.protocol.models.AirbyteStateMessage state) {
    return Jsons.object(Jsons.jsonNode(state), AirbyteStateMessage.class);
  }

  record StreamState(

                     AirbyteStateMessage.AirbyteStateType airbyteStateType,

                     List<AirbyteStateMessage> airbyteStateMessages) {

  }

}
