/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

/**
 * This class exists to track timing information for the sync. It needs to be thread-safe as
 * multiple threads (source, destination, and worker) will be accessing it.
 */
public class ThreadedTimeTracker {

  private long replicationStartTime;
  private long replicationEndTime;
  private long sourceReadStartTime;
  private long sourceReadEndTime;
  private long destinationWriteStartTime;
  private long destinationWriteEndTime;

  public synchronized void trackReplicationStartTime() {
    this.replicationStartTime = System.currentTimeMillis();
  }

  public synchronized void trackReplicationEndTime() {
    this.replicationEndTime = System.currentTimeMillis();
  }

  public synchronized void trackSourceReadStartTime() {
    this.sourceReadStartTime = System.currentTimeMillis();
  }

  public synchronized void trackSourceReadEndTime() {
    this.sourceReadEndTime = System.currentTimeMillis();
  }

  public synchronized void trackDestinationWriteStartTime() {
    this.destinationWriteStartTime = System.currentTimeMillis();
  }

  public synchronized void trackDestinationWriteEndTime() {
    this.destinationWriteEndTime = System.currentTimeMillis();
  }

  public synchronized long getReplicationStartTime() {
    return this.replicationStartTime;
  }

  public synchronized long getReplicationEndTime() {
    return this.replicationEndTime;
  }

  public synchronized long getSourceReadStartTime() {
    return this.sourceReadStartTime;
  }

  public synchronized long getSourceReadEndTime() {
    return this.sourceReadEndTime;
  }

  public synchronized long getDestinationWriteStartTime() {
    return this.destinationWriteStartTime;
  }

  public synchronized long getDestinationWriteEndTime() {
    return this.destinationWriteEndTime;
  }

}
