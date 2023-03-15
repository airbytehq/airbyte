/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

public class DynamodbUtils {

  private DynamodbUtils() {

  }

  public static DynamoDbClient createDynamoDbClient(final DynamodbConfig dynamodbConfig) {
    final var dynamoDbClientBuilder = DynamoDbClient.builder();

    // configure access credentials
    dynamoDbClientBuilder.credentialsProvider(StaticCredentialsProvider.create(
        AwsBasicCredentials.create(dynamodbConfig.accessKey(), dynamodbConfig.secretKey())));

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

  public static StreamState deserializeStreamState(final JsonNode state, final boolean useStreamCapableState) {
    final Optional<StateWrapper> typedState =
        StateMessageHelper.getTypedState(state, useStreamCapableState);
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
      if (useStreamCapableState) {
        return new StreamState(AirbyteStateMessage.AirbyteStateType.STREAM, List.of(
            new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState())));
      } else {
        return new StreamState(AirbyteStateMessage.AirbyteStateType.LEGACY, List.of(
            new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(Jsons.jsonNode(new DbState()))));
      }
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
