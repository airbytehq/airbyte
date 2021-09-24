/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This client caches only the results of spec jobs as their output should not change (except in the
 * case where the docker image is replaced with an image of the same name and tag) and they are
 * called very frequently.
 */
public class SpecCachingSynchronousSchedulerClient implements CachingSynchronousSchedulerClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(SpecCachingSynchronousSchedulerClient.class);

  private final Cache<String, SynchronousResponse<ConnectorSpecification>> specCache;
  private final SynchronousSchedulerClient decoratedClient;

  public SpecCachingSynchronousSchedulerClient(SynchronousSchedulerClient decoratedClient) {
    this.decoratedClient = decoratedClient;
    this.specCache = CacheBuilder.newBuilder().build();
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(final SourceConnection source, final String dockerImage)
      throws IOException {
    return decoratedClient.createSourceCheckConnectionJob(source, dockerImage);
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(final DestinationConnection destination,
                                                                                                final String dockerImage)
      throws IOException {
    return decoratedClient.createDestinationCheckConnectionJob(destination, dockerImage);
  }

  @Override
  public SynchronousResponse<AirbyteCatalog> createDiscoverSchemaJob(final SourceConnection source, final String dockerImage) throws IOException {
    return decoratedClient.createDiscoverSchemaJob(source, dockerImage);
  }

  @Override
  public SynchronousResponse<ConnectorSpecification> createGetSpecJob(String dockerImage) throws IOException {
    final Optional<SynchronousResponse<ConnectorSpecification>> cachedJob = Optional.ofNullable(specCache.getIfPresent(dockerImage));
    if (cachedJob.isPresent()) {
      LOGGER.debug("cache hit: " + dockerImage);
      return cachedJob.get();
    } else {
      LOGGER.debug("cache miss: " + dockerImage);
      final SynchronousResponse<ConnectorSpecification> response = decoratedClient.createGetSpecJob(dockerImage);
      if (response.isSuccess()) {
        specCache.put(dockerImage, response);
      }
      return response;
    }
  }

  @Override
  public void resetCache() {
    specCache.invalidateAll();
  }

}
