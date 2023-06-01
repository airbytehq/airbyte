/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Optional;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;

public interface Destination extends Integration {

  /**
   * Return a consumer that writes messages to the destination.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param catalog - schema of the incoming messages.
   * @return Consumer that accepts message. The {@link AirbyteMessageConsumer#accept(AirbyteMessage)}
   *         will be called n times where n is the number of messages.
   *         {@link AirbyteMessageConsumer#close()} will always be called once regardless of success
   *         or failure.
   * @throws Exception - any exception.
   */
  AirbyteMessageConsumer getConsumer(JsonNode config,
                                     ConfiguredAirbyteCatalog catalog,
                                     Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception;

  /**
   * Default implementation allows us to not have to touch existing destinations while avoiding a lot
   * of conditional statements in {@link IntegrationRunner}.
   *
   * @param config config
   * @param catalog catalog
   * @param outputRecordCollector outputRecordCollector
   * @return AirbyteMessageConsumer wrapped in SerializedAirbyteMessageConsumer to maintain legacy
   *         behavior.
   * @throws Exception exception
   */
  default SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                        final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return new ShimToSerializedAirbyteMessageConsumer(getConsumer(config, catalog, outputRecordCollector));
  }

  static void defaultOutputRecordCollector(final AirbyteMessage message) {
    System.out.println(Jsons.serialize(message));
  }

  /**
   * Backwards-compatibility wrapper for an AirbyteMessageConsumer. Strips the sizeInBytes argument
   * away from the .accept call.
   */
  @Slf4j
  class ShimToSerializedAirbyteMessageConsumer implements SerializedAirbyteMessageConsumer {

    private final AirbyteMessageConsumer consumer;

    public ShimToSerializedAirbyteMessageConsumer(final AirbyteMessageConsumer consumer) {
      this.consumer = consumer;
    }

    @Override
    public void start() throws Exception {
      consumer.start();
    }

    /**
     * Consumes an {@link AirbyteMessage} for processing.
     * <p>
     * If the provided JSON string is invalid AND represents a {@link AirbyteMessage.Type#STATE}
     * message, processing is halted. Otherwise, the invalid message is logged and execution continues.
     *
     * @param inputString JSON representation of an {@link AirbyteMessage}.
     * @throws Exception if an invalid state message is provided or the consumer is unable to accept the
     *         provided message.
     */
    @Override
    public void accept(final String inputString, final Integer sizeInBytes) throws Exception {
      consumeMessage(consumer, inputString);
    }

    @Override
    public void close() throws Exception {
      consumer.close();
    }

    /**
     * Consumes an {@link AirbyteMessage} for processing.
     * <p>
     * If the provided JSON string is invalid AND represents a {@link AirbyteMessage.Type#STATE}
     * message, processing is halted. Otherwise, the invalid message is logged and execution continues.
     *
     * @param consumer An {@link AirbyteMessageConsumer} that can handle the provided message.
     * @param inputString JSON representation of an {@link AirbyteMessage}.
     * @throws Exception if an invalid state message is provided or the consumer is unable to accept the
     *         provided message.
     */
    @VisibleForTesting
    static void consumeMessage(final AirbyteMessageConsumer consumer, final String inputString) throws Exception {

      final Optional<AirbyteMessage> messageOptional = Jsons.tryDeserialize(inputString, AirbyteMessage.class);
      if (messageOptional.isPresent()) {
        consumer.accept(messageOptional.get());
      } else {
        if (isStateMessage(inputString)) {
          throw new IllegalStateException("Invalid state message: " + inputString);
        } else {
          log.error("Received invalid message: " + inputString);
        }
      }
    }

    /**
     * Tests whether the provided JSON string represents a state message.
     *
     * @param input a JSON string that represents an {@link AirbyteMessage}.
     * @return {@code true} if the message is a state message, {@code false} otherwise.
     */
    @SuppressWarnings("OptionalIsPresent")
    private static boolean isStateMessage(final String input) {
      final Optional<AirbyteTypeMessage> deserialized = Jsons.tryDeserialize(input, AirbyteTypeMessage.class);
      if (deserialized.isPresent()) {
        return deserialized.get().getType() == Type.STATE;
      } else {
        return false;
      }
    }

    /**
     * Custom class for parsing a JSON message to determine the type of the represented
     * {@link AirbyteMessage}. Do the bare minimum deserialisation by reading only the type field.
     */
    private static class AirbyteTypeMessage {

      @JsonProperty("type")
      @JsonPropertyDescription("Message type")
      private AirbyteMessage.Type type;

      @JsonProperty("type")
      public AirbyteMessage.Type getType() {
        return type;
      }

      @JsonProperty("type")
      public void setType(final AirbyteMessage.Type type) {
        this.type = type;
      }

    }

  }

}
