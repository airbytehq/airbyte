/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.postgres.PostgresUtils.isCdc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

/**
 * A state manager for non resumable full refresh. It does not produce any meaningful state, but
 * just serves as feeding into SourceStateIterator so we can have counts.
 */
public class CtidCountStateManager implements SourceStateMessageProducer<AirbyteMessage> {

  final CtidStateManager ctidStateManager;
  final JsonNode config;

  public CtidCountStateManager(final JsonNode config,
                               final CtidStateManager ctidStateManager) {
    this.config = config;
    this.ctidStateManager = ctidStateManager;
  }

  @Nullable
  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(@Nullable ConfiguredAirbyteStream stream) {
    return null;
  }

  /**
   * @param stream
   * @param message
   * @return
   */
  @NotNull
  @Override
  public AirbyteMessage processRecordMessage(@Nullable ConfiguredAirbyteStream stream, AirbyteMessage message) {
    return message;
  }

  /**
   * @param stream
   * @return
   */
  @Nullable
  @Override
  public AirbyteStateMessage createFinalStateMessage(@Nullable ConfiguredAirbyteStream stream) {
    if (isCdc(config)) {
      return ctidStateManager.createFinalStateMessage(stream);
    } else {
      final AirbyteStreamState airbyteStreamState =
          new AirbyteStreamState()
              .withStreamDescriptor(
                  new StreamDescriptor()
                      .withName(stream.getStream().getName())
                      .withNamespace(stream.getStream().getNamespace()));

      return new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(airbyteStreamState);
    }
  }

  // no intermediate state message.
  @Override
  public boolean shouldEmitStateMessage(@Nullable ConfiguredAirbyteStream stream) {
    return false;
  }

}
