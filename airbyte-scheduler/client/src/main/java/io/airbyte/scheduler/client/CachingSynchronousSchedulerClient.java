/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

/**
 * This client is meant to be an interface over a cached implementation of
 * {@link SynchronousSchedulerClient}. It exposes functionality to allow invalidating the cache.
 */
public interface CachingSynchronousSchedulerClient extends SynchronousSchedulerClient {

  void resetCache();

}
