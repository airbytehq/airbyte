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
  private final ExecutorService producerPool;
  final BufferedWriter bufferedWriter;
  private boolean started;
  private final Lock lock;

  private final Runnable r = new Runnable() {

    @Override
    public void run() {
      final int sz = 100;
      final List<T> ll = new ArrayList<>(sz);
      while (true) {
        // LOGGER.info("*** thread: intrp {} sz {}", RecordWriter.this.producerPool.isShutdown(),
        // RecordWriter.this.messagesQueue.size());
        if (RecordWriter.this.producerPool.isShutdown() && RecordWriter.this.messagesQueue.peek() == null) {
          LOGGER.info("*** thread interrupted");
          ll.clear();
          break;
        }

        final int drained = RecordWriter.this.messagesQueue.drainTo(ll, sz);
        // LOGGER.debug("*** {} message drained", drained);
        if (drained == 0) {
          try {
            Thread.sleep(100);
          } catch (final InterruptedException e) {
            LOGGER.info("*** interrupt exception");
          }
        } else {
          for (int i = 0; i < drained; i++) {
            final String json = Jsons.serialize(ll.get(i));
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
    }

  };

  RecordWriter() {
    this(MSG_QUEUE_SIZE, PRODUCER_NUM_THREADS, WRITER_BUFFER_SIZE);
  }

  RecordWriter(final int messagesQueueSize, final int numThreads, final int writerBufferSize) {
    this.messagesQueueSize = messagesQueueSize;
    this.messagesQueue = new LinkedBlockingQueue<>(this.messagesQueueSize);
    this.numThreads = numThreads;
    this.producerPool = Executors.newFixedThreadPool(this.numThreads);
    this.bufferedWriter = new BufferedWriter(new OutputStreamWriter(System.out), writerBufferSize);
    this.started = false;
    this.lock = new ReentrantLock();

  }

  public void outputRecord(final T message) {
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

  public void drainQueuea() {

  }

  public void drainQueueAndOutputRecord(final T message) {

  }

  public void shutdownWorkers(final long timeout, final TimeUnit unit) throws InterruptedException, IOException {
    LOGGER.info("*** shutdownWorkers: {}", this.started);
    try {
      this.lock.lock();
      if (this.started) {
        LOGGER.info("*** shutdownNow");
        this.producerPool.shutdownNow(); // TODO: check here
        LOGGER.info("*** awaitTermination {} {}", timeout, unit.name());
        this.producerPool.awaitTermination(timeout, unit);
        LOGGER.info("*** done awaitTermination");
        synchronized (this.bufferedWriter) {
          this.bufferedWriter.close();
        }
        LOGGER.info("*** done writer close");
        this.started = false;
      }
    } finally {
      this.lock.unlock();
    }
    LOGGER.info("*** done shutdownWorkers");
  }

  public void startWorkers() throws IOException, InterruptedException {
    LOGGER.info("*** startWorkers: {}", this.started);
    try {
      this.lock.lock();
      if (!this.started) {
        // shutdownWorkers(1, TimeUnit.SECONDS); // TEMP
        startInternal();
      }
    } finally {
      this.lock.unlock();
    }
    LOGGER.info("*** done startWorkers");
  }

  private void startInternal() {
    for (int i = 0; i < this.numThreads; i++) {
      this.producerPool.execute(this.r);
    }
    this.started = true;
  }

}
