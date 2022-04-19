/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

public class S3Consumer extends FailureTrackingAirbyteMessageConsumer {

  private final S3DestinationConfig s3DestinationConfig;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final S3WriterFactory writerFactory;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, DestinationFileWriter> streamNameAndNamespaceToWriters;

  private AirbyteMessage lastStateMessage = null;

  public S3Consumer(final S3DestinationConfig s3DestinationConfig,
                    final ConfiguredAirbyteCatalog configuredCatalog,
                    final S3WriterFactory writerFactory,
                    final Consumer<AirbyteMessage> outputRecordCollector) {
    this.s3DestinationConfig = s3DestinationConfig;
    this.configuredCatalog = configuredCatalog;
    this.writerFactory = writerFactory;
    this.outputRecordCollector = outputRecordCollector;
    this.streamNameAndNamespaceToWriters = new HashMap<>(configuredCatalog.getStreams().size());
  }

  @Override
  protected void startTracked() throws Exception {
    final AmazonS3 s3Client = s3DestinationConfig.getS3Client();
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    for (final ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      final DestinationFileWriter writer = writerFactory
          .create(s3DestinationConfig, s3Client, configuredStream, uploadTimestamp);
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

    streamNameAndNamespaceToWriters.get(pair).write(UUID.randomUUID(), recordMessage);
  }

  @Override
  protected void close(final boolean hasFailed) throws Exception {
    for (final DestinationFileWriter handler : streamNameAndNamespaceToWriters.values()) {
      handler.close(hasFailed);
    }
    // S3 stream uploader is all or nothing if a failure happens in the destination.
    if (!hasFailed) {
      outputRecordCollector.accept(lastStateMessage);
    }
  }

}
