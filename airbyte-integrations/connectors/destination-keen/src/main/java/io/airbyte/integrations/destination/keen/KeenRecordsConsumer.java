/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.keen;

import static io.airbyte.integrations.destination.keen.KeenDestination.CONFIG_API_KEY;
import static io.airbyte.integrations.destination.keen.KeenDestination.CONFIG_PROJECT_ID;
import static io.airbyte.integrations.destination.keen.KeenDestination.INFER_TIMESTAMP;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KeenRecordsConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(KeenRecordsConsumer.class);

  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  private KeenTimestampService timestampService;
  private String projectId;
  private String apiKey;
  private KafkaProducer<String, String> kafkaProducer;
  private Set<String> streamNames;

  public KeenRecordsConsumer(final JsonNode config,
                             final ConfiguredAirbyteCatalog catalog,
                             final Consumer<AirbyteMessage> outputRecordCollector) {
    this.config = config;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.kafkaProducer = null;
    this.streamNames = Set.of();
    LOGGER.info("initializing consumer.");
  }

  @Override
  protected void startTracked() throws IOException, InterruptedException {
    projectId = config.get(CONFIG_PROJECT_ID).textValue();
    apiKey = config.get(CONFIG_API_KEY).textValue();
    final boolean timestampInferenceEnabled = Optional.ofNullable(config.get(INFER_TIMESTAMP))
        .map(JsonNode::booleanValue)
        .orElse(true);
    this.kafkaProducer = KeenDestination.KafkaProducerFactory.create(projectId, apiKey);
    this.streamNames = getStrippedStreamNames();
    this.timestampService = new KeenTimestampService(this.catalog, timestampInferenceEnabled);
    eraseOverwriteStreams();
  }

  @Override
  protected void acceptTracked(final AirbyteMessage msg) {
    if (msg.getType() == Type.STATE) {
      outputRecordCollector.accept(msg);
      return;
    } else if (msg.getType() != Type.RECORD) {
      return;
    }

    final String streamName = getStreamName(msg.getRecord());
    final JsonNode data = this.timestampService.injectTimestamp(msg.getRecord());

    kafkaProducer.send(new ProducerRecord<>(streamName, data.toString()));
  }

  private Set<String> getStrippedStreamNames() {
    return catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .map(KeenCharactersStripper::stripSpecialCharactersFromStreamName)
        .collect(Collectors.toSet());
  }

  private void eraseOverwriteStreams() throws IOException, InterruptedException {
    final KeenHttpClient keenHttpClient = new KeenHttpClient();
    LOGGER.info("erasing streams with override options selected.");

    final List<String> streamsToDelete = this.catalog.getStreams().stream()
        .filter(stream -> stream.getDestinationSyncMode() == DestinationSyncMode.OVERWRITE)
        .map(stream -> KeenCharactersStripper.stripSpecialCharactersFromStreamName(stream.getStream().getName()))
        .collect(Collectors.toList());

    for (final String streamToDelete : streamsToDelete) {
      LOGGER.info("erasing stream " + streamToDelete);
      keenHttpClient.eraseStream(streamToDelete, projectId, apiKey);
    }
  }

  private String getStreamName(final AirbyteRecordMessage recordMessage) {
    String streamName = recordMessage.getStream();
    if (streamNames.contains(streamName)) {
      return streamName;
    }
    streamName = KeenCharactersStripper.stripSpecialCharactersFromStreamName(streamName);
    if (!streamNames.contains(streamName)) {
      throw new IllegalArgumentException(
          String.format(
              "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
    }
    return streamName;
  }

  @Override
  protected void close(final boolean hasFailed) {
    kafkaProducer.flush();
    kafkaProducer.close();
  }

}
