/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import com.google.cloud.storage.Blob;
import com.google.cloud.storage.Storage;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteProtocolSchema;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsBucketSpecFetcher {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsBucketSpecFetcher.class);

  private final Storage storage;
  private final String bucketName;

  public GcsBucketSpecFetcher(final Storage storage, final String bucketName) {
    this.storage = storage;
    this.bucketName = bucketName;
  }

  public String getBucketName() {
    return bucketName;
  }

  public Optional<ConnectorSpecification> attemptFetch(final String dockerImage) {
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
      LOGGER.error("Received invalid spec from bucket store. {}", e.toString());
      return Optional.empty();
    }
    return Optional.of(Jsons.deserialize(specAsString, ConnectorSpecification.class));
  }

  private static void validateConfig(final JsonNode json) throws JsonValidationException {
    final JsonSchemaValidator jsonSchemaValidator = new JsonSchemaValidator();
    final JsonNode specJsonSchema = JsonSchemaValidator.getSchema(AirbyteProtocolSchema.PROTOCOL.getFile(), "ConnectorSpecification");
    jsonSchemaValidator.ensure(specJsonSchema, json);
  }

}
