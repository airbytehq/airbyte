/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.gcs.writer.GcsWriterFactory;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsConsumer extends FailureTrackingAirbyteMessageConsumer {

  protected static final Logger LOGGER = LoggerFactory.getLogger(GcsConsumer.class);

  private final GcsDestinationConfig gcsDestinationConfig;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final GcsWriterFactory writerFactory;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, DestinationFileWriter> streamNameAndNamespaceToWriters;

  private AirbyteMessage lastStateMessage = null;

  public GcsConsumer(final GcsDestinationConfig gcsDestinationConfig,
                     final ConfiguredAirbyteCatalog configuredCatalog,
                     final GcsWriterFactory writerFactory,
                     final Consumer<AirbyteMessage> outputRecordCollector) {
    this.gcsDestinationConfig = gcsDestinationConfig;
    this.configuredCatalog = configuredCatalog;
    this.writerFactory = writerFactory;
    this.outputRecordCollector = outputRecordCollector;
    this.streamNameAndNamespaceToWriters = new HashMap<>(configuredCatalog.getStreams().size());
  }

  @Override
  protected void startTracked() throws Exception {
    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    for (final ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      final DestinationFileWriter writer = writerFactory
          .create(gcsDestinationConfig, s3Client, configuredStream, uploadTimestamp);
      writer.initialize();

      final AirbyteStream stream = configuredStream.getStream();
      final AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair
          .fromAirbyteSteam(stream);
      streamNameAndNamespaceToWriters.put(streamNamePair, writer);
    }
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) throws Exception {
    if (airbyteMessage.getType() == Type.STATE) {
      this.lastStateMessage = airbyteMessage;
      return;
    } else if (airbyteMessage.getType() != Type.RECORD) {
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

    final UUID id = UUID.randomUUID();
    streamNameAndNamespaceToWriters.get(pair).write(id, recordMessage);
  }

  @Override
  protected void close(final boolean hasFailed) throws Exception {
    LOGGER.debug("Closing consumer with writers = {}", streamNameAndNamespaceToWriters);
    List<Exception> exceptionsThrown = new ArrayList<>();
    for (var entry : streamNameAndNamespaceToWriters.entrySet()) {
      final DestinationFileWriter handler = entry.getValue();
      LOGGER.debug("Closing writer {}", entry.getKey());
      try {
        handler.close(hasFailed);
      } catch (Exception e) {
        exceptionsThrown.add(e);
        LOGGER.error("Exception while closing writer {}", entry.getKey(), e);
      }
    }
    if (!exceptionsThrown.isEmpty()) {
      throw new RuntimeException(String.format("Exceptions thrown while closing consumer: %s", Strings.join(exceptionsThrown, "\n")));
    }
    // Gcs stream uploader is all or nothing if a failure happens in the destination.
    if (!hasFailed) {
      outputRecordCollector.accept(lastStateMessage);
    }
  }

}
