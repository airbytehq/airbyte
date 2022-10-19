/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pubsub;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.pubsub.v1.Publisher;
import com.google.common.base.Charsets;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import com.google.protobuf.ByteString;
import com.google.pubsub.v1.PubsubMessage;
import com.google.pubsub.v1.TopicName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.ByteArrayInputStream;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PubsubConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(PubsubConsumer.class);
  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, Map<String, String>> attributes;
  private Publisher publisher;

  public PubsubConsumer(final JsonNode config,
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
    final String projectId = config.get(PubsubDestination.CONFIG_PROJECT_ID).asText();
    final String topicName = config.get(PubsubDestination.CONFIG_TOPIC_ID).asText();
    final TopicName topic = TopicName.of(projectId, topicName);
    final String credentialsString =
        config.get(PubsubDestination.CONFIG_CREDS).isObject() ? Jsons.serialize(config.get(
            PubsubDestination.CONFIG_CREDS))
            : config.get(PubsubDestination.CONFIG_CREDS).asText();
    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));
    publisher = Publisher.newBuilder(topic)
        .setEnableMessageOrdering(true)
        .setCredentialsProvider(FixedCredentialsProvider.create(credentials)).build();
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final Map<String, String> attrs = Maps.newHashMap();
      final var key = AirbyteStreamNameNamespacePair.fromAirbyteSteam(configStream.getStream());
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

    publisher.publish(
        PubsubMessage.newBuilder().putAllAttributes(attributes.get(streamKey))
            .setOrderingKey(streamKey.toString())
            .setData(ByteString.copyFromUtf8(Jsons.serialize(data))).build());
  }

  @Override
  protected void close(final boolean hasFailed) throws Exception {
    if (!hasFailed) {
      publisher.shutdown();
      LOGGER.info("shutting down consumer.");
    }
  }

}
