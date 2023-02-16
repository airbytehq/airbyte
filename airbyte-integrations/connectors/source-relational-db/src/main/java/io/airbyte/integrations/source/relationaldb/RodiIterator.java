package io.airbyte.integrations.source.relationaldb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.AbstractDatabase;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Iterator;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import javax.annotation.CheckForNull;
import org.apache.commons.lang3.tuple.Pair;
import org.postgresql.core.Tuple;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RodiIterator extends AbstractIterator<AirbyteMessage> {
  private static final Logger LOGGER = LoggerFactory.getLogger(RodiIterator.class);
  private static final int NUM_THREADS = 4;
  private final Iterator<Tuple> messageIterator;
  private final BlockingQueue<AirbyteMessage> messageQueue;
  private final ExecutorService pool;
  private boolean running;
  CheckedFunction<Pair<Tuple, ResultSetMetaData>, JsonNode, SQLException> rowTransform;
  final String streamName;
  final String namespace;
  final long emittedAt;
  boolean done;
  ResultSetMetaData metaData;
  final AbstractDatabase database;

  public RodiIterator(final AbstractDatabase database, final Iterator<Tuple> messageIterator, final CheckedFunction<Pair<Tuple, ResultSetMetaData>, JsonNode, SQLException> rowTransform,
      final String streamName,
      final String namespace,
      final long emittedAt) {
    this.messageIterator = messageIterator;
    this.messageQueue = new LinkedBlockingQueue<>(500_000);
    this.pool = Executors.newFixedThreadPool(NUM_THREADS);
    this.running = false;
    this.rowTransform = rowTransform;
    this.streamName = streamName;
    this.namespace = namespace;
    this.emittedAt = emittedAt;
    this.done = false;
    this.database = database;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    if (!running && !done) {
      final Runnable r = () -> {
        while (true) {
          Tuple row = null;
//          synchronized (messageIterator) {

            if (messageIterator.hasNext()) {
              row = messageIterator.next();
//              LOGGER.info("*** row from iterator {} bytes", row.length());
              if (RodiIterator.this.metaData == null) {
                RodiIterator.this.metaData = RodiIterator.this.database.currentMetaData;
              }

            } else {
              LOGGER.info("*** no more hasNext");
              running = false;
              done = true;
              break;
            }
//          }
          if (row != null) {
            try {
//              LOGGER.info("*** transform to JsonNode: {} {} {}", row, rowTransform, RodiIterator.this.metaData);
              final JsonNode node = rowTransform.apply(Pair.of(row, RodiIterator.this.metaData));
//              LOGGER.info("*** JsonNode: {}", node);
              final AirbyteMessage message = new AirbyteMessage().withType(Type.RECORD).withRecord(new AirbyteRecordMessage().withStream(streamName)
                  .withNamespace(namespace)
                  .withEmittedAt(emittedAt)
                  .withData(node)
                  .withJsonString(Jsons.serialize(node)));
              message.getRecord().setJsonString(Jsons.serialize(message));
              message.getRecord().setData(null);
              while (!messageQueue.offer(message, 100, TimeUnit.MILLISECONDS)) {
                LOGGER.info("*** offerring queue");
              }
            } catch (final InterruptedException | SQLException ex) {
              LOGGER.info("*** err", ex);
            }
            row = null;
          }
        }
      };
      LOGGER.info("*** num cores {}", Runtime.getRuntime().availableProcessors());
      for (int i = 0; i < NUM_THREADS; i++) {
        this.pool.submit(r);
      }
      running = true;

//      try {
//        Thread.sleep(1000);
//      } catch (final InterruptedException e) {
//        throw new RuntimeException(e);
//      }

    }

    AirbyteMessage message = null;
    try {
      message = messageQueue.poll(100, TimeUnit.MILLISECONDS);
    } catch (final InterruptedException e) {
      throw new RuntimeException(e);
    }
    while (message == null && !done) {
      LOGGER.info("*** no message in queue");
      message = messageQueue.poll();
    }

    if (message != null) {
//      LOGGER.info("*** return message");
      return message;
    } else {
      LOGGER.info("*** return endOfData");
      pool.shutdown();
      try {
        pool.awaitTermination(2, TimeUnit.SECONDS);
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }
      return endOfData();
    }
  }
}
