/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.specs;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import com.google.cloud.storage.Blob;
import com.google.cloud.storage.Storage;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs.DeploymentMode;
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

  // these filenames must match default_spec_file and cloud_spec_file in manage.sh
  public static final String DEFAULT_SPEC_FILE = "spec.json";
  public static final String CLOUD_SPEC_FILE = "spec.cloud.json";

  private final Storage storage;
  private final String bucketName;
  private final DeploymentMode deploymentMode;

  public GcsBucketSpecFetcher(final Storage storage, final String bucketName) {
    this.storage = storage;
    this.bucketName = bucketName;
    this.deploymentMode = DeploymentMode.OSS;
  }

  /**
   * This constructor is used by airbyte-cloud to fetch cloud-specific spec files.
   */
  public GcsBucketSpecFetcher(final Storage storage, final String bucketName, final DeploymentMode deploymentMode) {
    this.storage = storage;
    this.bucketName = bucketName;
    this.deploymentMode = deploymentMode;
  }

  public String getBucketName() {
    return bucketName;
  }

  public Optional<ConnectorSpecification> attemptFetch(final String dockerImage) {
    final String[] dockerImageComponents = dockerImage.split(":");
    Preconditions.checkArgument(dockerImageComponents.length == 2, "Invalidate docker image: " + dockerImage);
    final String dockerImageName = dockerImageComponents[0];
    final String dockerImageTag = dockerImageComponents[1];

    final Optional<Blob> specAsBlob = getSpecAsBlob(dockerImageName, dockerImageTag);

    if (specAsBlob.isEmpty()) {
      LOGGER.debug("Spec not found in bucket storage");
      return Optional.empty();
    }

    final String specAsString = new String(specAsBlob.get().getContent(), StandardCharsets.UTF_8);
    try {
      validateConfig(Jsons.deserialize(specAsString));
    } catch (final JsonValidationException e) {
      LOGGER.error("Received invalid spec from bucket store. {}", e.toString());
      return Optional.empty();
    }
    return Optional.of(Jsons.deserialize(specAsString, ConnectorSpecification.class));
  }

  @VisibleForTesting
  Optional<Blob> getSpecAsBlob(final String dockerImageName, final String dockerImageTag) {
    if (deploymentMode == DeploymentMode.CLOUD) {
      final Optional<Blob> cloudSpecAsBlob = getSpecAsBlob(dockerImageName, dockerImageTag, CLOUD_SPEC_FILE, DeploymentMode.CLOUD);
      if (cloudSpecAsBlob.isPresent()) {
        LOGGER.info("Found cloud specific spec: {} {}", bucketName, cloudSpecAsBlob);
        return cloudSpecAsBlob;
      }
    }
    return getSpecAsBlob(dockerImageName, dockerImageTag, DEFAULT_SPEC_FILE, DeploymentMode.OSS);
  }

  @VisibleForTesting
  Optional<Blob> getSpecAsBlob(final String dockerImageName,
                               final String dockerImageTag,
                               final String specFile,
                               final DeploymentMode deploymentMode) {
    final Path specPath = Path.of("specs").resolve(dockerImageName).resolve(dockerImageTag).resolve(specFile);
    LOGGER.debug("Checking path for cached {} spec: {} {}", deploymentMode.name(), bucketName, specPath);
    final Blob specAsBlob = storage.get(bucketName, specPath.toString());
    if (specAsBlob != null) {
      return Optional.of(specAsBlob);
    }
    return Optional.empty();
  }

  private static void validateConfig(final JsonNode json) throws JsonValidationException {
    final JsonSchemaValidator jsonSchemaValidator = new JsonSchemaValidator();
    final JsonNode specJsonSchema = JsonSchemaValidator.getSchema(AirbyteProtocolSchema.PROTOCOL.getFile(), "ConnectorSpecification");
    jsonSchemaValidator.ensure(specJsonSchema, json);
  }

}
