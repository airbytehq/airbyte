/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import com.google.cloud.storage.StorageOptions;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.specs.GcsBucketSpecFetcher;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BucketSpecCacheSchedulerClient implements SynchronousSchedulerClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(BucketSpecCacheSchedulerClient.class);

  private final SynchronousSchedulerClient client;
  private final GcsBucketSpecFetcher bucketSpecFetcher;

  public BucketSpecCacheSchedulerClient(final SynchronousSchedulerClient client, final String bucketName) {
    this.client = client;
    this.bucketSpecFetcher = new GcsBucketSpecFetcher(StorageOptions.getDefaultInstance().getService(), bucketName);
  }

  @VisibleForTesting
  BucketSpecCacheSchedulerClient(final SynchronousSchedulerClient client, final GcsBucketSpecFetcher bucketSpecFetcher) {
    this.client = client;
    this.bucketSpecFetcher = bucketSpecFetcher;
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(final SourceConnection source, final String dockerImage)
      throws IOException {
    return client.createSourceCheckConnectionJob(source, dockerImage);
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(final DestinationConnection destination,
                                                                                                final String dockerImage)
      throws IOException {
    return client.createDestinationCheckConnectionJob(destination, dockerImage);
  }

  @Override
  public SynchronousResponse<AirbyteCatalog> createDiscoverSchemaJob(final SourceConnection source, final String dockerImage) throws IOException {
    return client.createDiscoverSchemaJob(source, dockerImage);
  }

  @Override
  public SynchronousResponse<ConnectorSpecification> createGetSpecJob(final String dockerImage) throws IOException {
    LOGGER.debug("getting spec!");
    Optional<ConnectorSpecification> cachedSpecOptional;
    // never want to fail because we could not fetch from off board storage.
    try {
      cachedSpecOptional = bucketSpecFetcher.attemptFetch(dockerImage);
      LOGGER.debug("Spec bucket cache: Call to cache did not fail.");
    } catch (final RuntimeException e) {
      cachedSpecOptional = Optional.empty();
      LOGGER.debug("Spec bucket cache: Call to cache failed.");
    }

    if (cachedSpecOptional.isPresent()) {
      LOGGER.debug("Spec bucket cache: Cache hit.");
      return new SynchronousResponse<>(cachedSpecOptional.get(), SynchronousJobMetadata.mock(ConfigType.GET_SPEC));
    } else {
      LOGGER.debug("Spec bucket cache: Cache miss.");
      return client.createGetSpecJob(dockerImage);
    }
  }

}
