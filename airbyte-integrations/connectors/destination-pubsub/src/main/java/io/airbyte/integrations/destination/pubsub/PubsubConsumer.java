/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pubsub;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.cloud.pubsub.v1.Publisher;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import com.google.protobuf.ByteString;
import com.google.pubsub.v1.PubsubMessage;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PubsubConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(PubsubConsumer.class);
  private final PubsubDestinationConfig config;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, Map<String, String>> attributes;
  private Publisher publisher;

  public PubsubConsumer(final PubsubDestinationConfig config,
                        final ConfiguredAirbyteCatalog catalog,
                        final Consumer<AirbyteMessage> outputRecordCollector) {
    this.outputRecordCollector = outputRecordCollector;
    this.config = config;
    this.catalog = catalog;
    this.attributes = Maps.newHashMap();
    this.publisher = null;
    LOGGER.info("initializing consumer.");
  }

  @Override
  protected void startTracked() throws Exception {
    // get publisher
    publisher = Publisher.newBuilder(config.getTopic())
        .setBatchingSettings(config.getBatchingSettings())
        .setEnableMessageOrdering(config.isOrderingEnabled())
        .setCredentialsProvider(FixedCredentialsProvider.create(config.getCredentials()))
        .build();
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final Map<String, String> attrs = Maps.newHashMap();
      final var key = AirbyteStreamNameNamespacePair.fromAirbyteStream(configStream.getStream());
      attrs.put(PubsubDestination.STREAM, key.getName());
      if (!Strings.isNullOrEmpty(key.getNamespace())) {
        attrs.put(PubsubDestination.NAMESPACE, key.getNamespace());
      }
      attributes.put(key, attrs);
    }
  }

  @Override
  protected void acceptTracked(final AirbyteMessage msg) throws Exception {
    if (msg.getType() == Type.STATE) {
      outputRecordCollector.accept(msg);
      return;
    } else if (msg.getType() != Type.RECORD) {
      return;
    }
    final AirbyteRecordMessage recordMessage = msg.getRecord();
    final AirbyteStreamNameNamespacePair streamKey = AirbyteStreamNameNamespacePair
        .fromRecordMessage(recordMessage);

    if (!attributes.containsKey(streamKey)) {
      throw new IllegalArgumentException(
          String.format(
              "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
    }
    final JsonNode data = Jsons.jsonNode(ImmutableMap.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData(),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt()));

    var messageBuilder = PubsubMessage.newBuilder()
        .putAllAttributes(attributes.get(streamKey))
        .setData(ByteString.copyFromUtf8(Jsons.serialize(data)));
    if (config.isOrderingEnabled()) {
      messageBuilder.setOrderingKey(streamKey.toString());
    }
    publisher.publish(messageBuilder.build());
  }

  @Override
  protected void close(final boolean hasFailed) throws Exception {
    if (!hasFailed) {
      publisher.shutdown();
      LOGGER.info("shutting down consumer.");
    }
  }

}
