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
  private AirbyteMessage lastStateMessage;
  private Set<String> streamNames;

  public KeenRecordsConsumer(JsonNode config,
                             ConfiguredAirbyteCatalog catalog,
                             Consumer<AirbyteMessage> outputRecordCollector) {
    this.config = config;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.kafkaProducer = null;
    this.streamNames = Set.of();
    this.lastStateMessage = null;
    LOGGER.info("initializing consumer.");
  }

  @Override
  protected void startTracked() throws IOException, InterruptedException {
    projectId = config.get(CONFIG_PROJECT_ID).textValue();
    apiKey = config.get(CONFIG_API_KEY).textValue();
    boolean timestampInferenceEnabled = Optional.ofNullable(config.get(INFER_TIMESTAMP))
        .map(JsonNode::booleanValue)
        .orElse(true);
    this.kafkaProducer = KeenDestination.KafkaProducerFactory.create(projectId, apiKey);
    this.streamNames = getStrippedStreamNames();
    this.timestampService = new KeenTimestampService(this.catalog, timestampInferenceEnabled);
    eraseOverwriteStreams();
  }

  @Override
  protected void acceptTracked(AirbyteMessage msg) {
    if (msg.getType() == Type.STATE) {
      lastStateMessage = msg;
      outputRecordCollector.accept(lastStateMessage);
      return;
    } else if (msg.getType() != Type.RECORD) {
      return;
    }

    final String streamName = getStreamName(msg.getRecord());
    JsonNode data = this.timestampService.injectTimestamp(msg.getRecord());

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
    KeenHttpClient keenHttpClient = new KeenHttpClient();
    LOGGER.info("erasing streams with override options selected.");

    List<String> streamsToDelete = this.catalog.getStreams().stream()
        .filter(stream -> stream.getDestinationSyncMode() == DestinationSyncMode.OVERWRITE)
        .map(stream -> KeenCharactersStripper.stripSpecialCharactersFromStreamName(stream.getStream().getName()))
        .collect(Collectors.toList());

    for (String streamToDelete : streamsToDelete) {
      LOGGER.info("erasing stream " + streamToDelete);
      keenHttpClient.eraseStream(streamToDelete, projectId, apiKey);
    }
  }

  private String getStreamName(AirbyteRecordMessage recordMessage) {
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
  protected void close(boolean hasFailed) {
    kafkaProducer.flush();
    kafkaProducer.close();
    if (!hasFailed) {
      outputRecordCollector.accept(lastStateMessage);
    }
  }

}
