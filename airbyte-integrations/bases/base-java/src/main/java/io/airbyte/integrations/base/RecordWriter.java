/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.commons.json.Jsons;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RecordWriter<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(RecordWriter.class);
  private static final int MSG_QUEUE_SIZE = 1_000_000;
  private static final int PRODUCER_NUM_THREADS = 3;
  private static final int WRITER_BUFFER_SIZE = 100_000;
  private final int messagesQueueSize;
  private final BlockingQueue<T> messagesQueue;
  private final int numThreads;
  private ExecutorService producerPool;
  private final int writerBufferSize;
  final private BufferedWriter bufferedWriter;
  private boolean started;
  private final Lock lock;

  private final Runnable r = new Runnable() {

    @Override
    public void run() {
      final int maxObjectsFromQueue = 50;
      final List<T> queueObjects = new ArrayList<>(maxObjectsFromQueue);
      while (true) {
        if (RecordWriter.this.producerPool.isShutdown() && RecordWriter.this.messagesQueue.peek() == null) {
          LOGGER.debug("*** thread interrupted");
          queueObjects.clear();
          break;
        }

        final int drained = RecordWriter.this.messagesQueue.drainTo(queueObjects, maxObjectsFromQueue);
         LOGGER.debug("*** {} message drained", drained);
        if (drained == 0) {
          try {
            Thread.sleep(100);
          } catch (final InterruptedException e) {
            LOGGER.debug("*** interrupt exception");
          }
        } else {
          for (int i = 0; i < drained; i++) {
            final String json = Jsons.serialize(queueObjects.get(i));
            LOGGER.debug("*** msg from queue: {}", json);
            synchronized (RecordWriter.this.bufferedWriter) {
              try {
                RecordWriter.this.bufferedWriter.write(json);
                RecordWriter.this.bufferedWriter.newLine();
              } catch (final IOException e) {
                LOGGER.info("*** unable to write out: ", e);
                // throw new RuntimeException(e);
              }
            }
          }
        }
      }
      synchronized (RecordWriter.this.bufferedWriter) {
        try {
          RecordWriter.this.bufferedWriter.flush();
        } catch (final IOException e) {
          throw new RuntimeException(e);
        }
      }
    }

  };

  RecordWriter() {
    this(MSG_QUEUE_SIZE, PRODUCER_NUM_THREADS, WRITER_BUFFER_SIZE);
  }

  RecordWriter(final int messagesQueueSize, final int numThreads, final int writerBufferSize) {
    this.messagesQueueSize = messagesQueueSize;
    this.messagesQueue = new LinkedBlockingQueue<>(this.messagesQueueSize);
    this.numThreads = numThreads;
    this.started = false;
    this.writerBufferSize = writerBufferSize;
    this.bufferedWriter = new BufferedWriter(new OutputStreamWriter(System.out), this.writerBufferSize);
    this.lock = new ReentrantLock();

  }

  public void outputRecord(final T message) {
    outputRecord_internal(message);
  }

  private void outputRecord_internal(final T message) {
    if (!started) {
      try {
        startWorkers();
      } catch (final IOException | InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
    try {
      while (!this.messagesQueue.offer(message, 1, TimeUnit.SECONDS)) {
        LOGGER.debug("***");
      }
    } catch (final InterruptedException e) {
      LOGGER.debug("***");
    }
  }

  public void drainQueueAndOutputRecord(final T message) {
    drainQueueAndOutputRecord_internal(message);
  }

  private void drainQueueAndOutputRecord_internal(final T message) {

    try {
      LOGGER.debug("*** draining queue");
      shutdownWorkers(1, TimeUnit.MINUTES);
      LOGGER.debug("*** queue drained -- writing out");
      outputRecord_internal(message);
    } catch (final InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }

  }

  public void shutdownWorkers(final long timeout, final TimeUnit unit) throws InterruptedException, IOException {
    LOGGER.debug("*** shutdownWorkers: {}", this.started);
    try {
      this.lock.lock();
      if (this.started) {
        LOGGER.debug("*** shutdownNow");
        this.producerPool.shutdownNow(); // TODO: check here
        LOGGER.debug("*** awaitTermination {} {}", timeout, unit.name());
        this.producerPool.awaitTermination(timeout, unit);
        LOGGER.debug("*** done awaitTermination");
        this.started = false;
      }
    } finally {
      this.lock.unlock();
    }
    LOGGER.debug("*** done shutdownWorkers");
  }

  public void startWorkers() throws IOException, InterruptedException {
    LOGGER.debug("*** startWorkers: {}", this.started);
    try {
      this.lock.lock();
      if (!this.started) {
        startInternal();
      }
    } finally {
      this.lock.unlock();
    }
    LOGGER.debug("*** done startWorkers");
  }

  private void startInternal() {
    this.producerPool = Executors.newFixedThreadPool(this.numThreads);
    for (int i = 0; i < this.numThreads; i++) {
      this.producerPool.execute(this.r);
    }
    this.started = true;
  }

}
