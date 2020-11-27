package io.airbyte.integrations.base;

import com.google.common.base.Charsets;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RecordConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumer<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(RecordConsumer.class);

  private static final long THREAD_DELAY_MILLIS = 500L;

  private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
  private static final int MIN_RECORDS = 500;
  private static final int BATCH_SIZE = 500;

  private final DestinationConsumerCallback destination;
  private final Map<String, WriteConfig> writeConfigs;
  private final ConfiguredAirbyteCatalog catalog;
  private final ScheduledExecutorService writerPool;


  public RecordConsumer(DestinationConsumerCallback destination, Map<String, WriteConfig> writeConfigs, ConfiguredAirbyteCatalog catalog) {
    this.destination = destination;
    this.writeConfigs = writeConfigs;
    this.catalog = catalog;
    this.writerPool = Executors.newSingleThreadScheduledExecutor();
    Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofMinutes(GRACEFUL_SHUTDOWN_MINUTES), writerPool));

    writerPool.scheduleWithFixedDelay(
        () -> writeStreamsWithNRecords(MIN_RECORDS, BATCH_SIZE, writeConfigs, destination),
        THREAD_DELAY_MILLIS,
        THREAD_DELAY_MILLIS,
        TimeUnit.MILLISECONDS);
  }

  /**
   * Write records from buffer to destination in batch.
   *
   * @param minRecords - the minimum number of records in the buffer before writing. helps avoid
   *        wastefully writing one record at a time.
   * @param batchSize - the maximum number of records to write in a single insert.
   * @param writeBuffers - map of stream name to its respective buffer.
   * @param destination - Connection to destination
   */
  private static void writeStreamsWithNRecords(int minRecords, int batchSize,
      Map<String, WriteConfig> writeBuffers,
      DestinationConsumerCallback destination) {
    for (final Map.Entry<String, WriteConfig> entry : writeBuffers.entrySet()) {
      final String schemaName = entry.getValue().getSchemaName();
      final String tmpTableName = entry.getValue().getTmpTableName();
      final CloseableQueue<byte[]> writeBuffer = entry.getValue().getWriteBuffer();
      while (writeBuffer.size() > minRecords) {
        destination.writeQuery(batchSize, writeBuffer, schemaName, tmpTableName);
      }
    }
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) throws Exception {
    // ignore other message types.
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      if (!writeConfigs.containsKey(message.getRecord().getStream())) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(message)));
      }
      writeConfigs.get(message.getRecord().getStream()).getWriteBuffer().offer(Jsons.serialize(message.getRecord()).getBytes(Charsets.UTF_8));
    }
  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    if (hasFailed) {
      LOGGER.error("executing on failed close procedure.");

      // kill executor pool fast.
      writerPool.shutdown();
      writerPool.awaitTermination(1, TimeUnit.SECONDS);
    } else {
      LOGGER.info("executing on success close procedure.");

      // shutdown executor pool with time to complete writes.
      writerPool.shutdown();
      writerPool.awaitTermination(GRACEFUL_SHUTDOWN_MINUTES, TimeUnit.MINUTES);

      // write anything that is left in the buffers.
      writeStreamsWithNRecords(0, 500, writeConfigs, destination);

      destination.commitRawTables(writeConfigs);
    }

    // close buffers.
    for (final WriteConfig writeContext : writeConfigs.values()) {
      writeContext.getWriteBuffer().close();
    }
    destination.cleanupTmpTables(writeConfigs);
  }
}
