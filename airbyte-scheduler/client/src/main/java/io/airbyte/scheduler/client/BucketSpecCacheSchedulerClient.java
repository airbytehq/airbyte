/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.scheduler.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import com.google.cloud.storage.Blob;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteProtocolSchema;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BucketSpecCacheSchedulerClient implements SynchronousSchedulerClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(BucketSpecCacheSchedulerClient.class);

  private final SynchronousSchedulerClient client;
  private final Function<String, Optional<ConnectorSpecification>> bucketSpecFetcher;

  public BucketSpecCacheSchedulerClient(final SynchronousSchedulerClient client, final String bucketName) {
    this(
        client,
        dockerImage -> attemptToFetchSpecFromBucket(StorageOptions.getDefaultInstance().getService(), bucketName, dockerImage));
  }

  @VisibleForTesting
  BucketSpecCacheSchedulerClient(final SynchronousSchedulerClient client,
                                 final Function<String, Optional<ConnectorSpecification>> bucketSpecFetcher) {
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
      cachedSpecOptional = bucketSpecFetcher.apply(dockerImage);
      LOGGER.debug("Spec bucket cache: Call to cache did not fail.");
    } catch (final RuntimeException e) {
      cachedSpecOptional = Optional.empty();
      LOGGER.debug("Spec bucket cache: Call to cache failed.");
    }

    if (cachedSpecOptional.isPresent()) {
      LOGGER.debug("Spec bucket cache: Cache hit.");
      final long now = Instant.now().toEpochMilli();
      final SynchronousJobMetadata mockMetadata = new SynchronousJobMetadata(
          UUID.randomUUID(),
          ConfigType.GET_SPEC,
          null,
          now,
          now,
          true,
          Path.of(""));
      return new SynchronousResponse<>(cachedSpecOptional.get(), mockMetadata);
    } else {
      LOGGER.debug("Spec bucket cache: Cache miss.");
      return client.createGetSpecJob(dockerImage);
    }
  }

  private static void validateConfig(final JsonNode json) throws JsonValidationException {
    final JsonSchemaValidator jsonSchemaValidator = new JsonSchemaValidator();
    final JsonNode specJsonSchema = JsonSchemaValidator.getSchema(AirbyteProtocolSchema.PROTOCOL.getFile(), "ConnectorSpecification");
    jsonSchemaValidator.ensure(specJsonSchema, json);
  }

  private static Optional<ConnectorSpecification> attemptToFetchSpecFromBucket(final Storage storage,
                                                                               final String bucketName,
                                                                               final String dockerImage) {
    final String[] dockerImageComponents = dockerImage.split(":");
    Preconditions.checkArgument(dockerImageComponents.length == 2, "Invalidate docker image: " + dockerImage);
    final String dockerImageName = dockerImageComponents[0];
    final String dockerImageTag = dockerImageComponents[1];

    final Path specPath = Path.of("specs").resolve(dockerImageName).resolve(dockerImageTag).resolve("spec.json");
    LOGGER.debug("Checking path for cached spec: {} {}", bucketName, specPath);
    final Blob specAsBlob = storage.get(bucketName, specPath.toString());

    // if null it means the object was not found.
    if (specAsBlob == null) {
      LOGGER.debug("Spec not found in bucket storage");
      return Optional.empty();
    }

    final String specAsString = new String(specAsBlob.getContent(), StandardCharsets.UTF_8);
    try {
      validateConfig(Jsons.deserialize(specAsString));
    } catch (final JsonValidationException e) {
      LOGGER.error("Received invalid spec from bucket store. Received: {}", specAsString);
      return Optional.empty();
    }
    return Optional.of(Jsons.deserialize(specAsString, ConnectorSpecification.class));
  }

}
