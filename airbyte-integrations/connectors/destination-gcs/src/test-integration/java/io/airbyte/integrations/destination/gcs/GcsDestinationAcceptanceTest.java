/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * When adding a new GCS destination acceptance test, extend this class and do the following:
 * <li>Implement {@link #getFormatConfig} that returns a {@link S3FormatConfig}</li>
 * <li>Implement {@link #retrieveRecords} that returns the Json records for the test</li>
 *
 * Under the hood, a {@link io.airbyte.integrations.destination.gcs.GcsDestinationConfig} is
 * constructed as follows:
 * <li>Retrieve the secrets from "secrets/config.json"</li>
 * <li>Get the GCS bucket path from the constructor</li>
 * <li>Get the format config from {@link #getFormatConfig}</li>
 */
public abstract class GcsDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected static final Logger LOGGER = LoggerFactory.getLogger(GcsDestinationAcceptanceTest.class);
  protected static final ObjectMapper MAPPER = MoreMappers.initMapper();

  protected static final String SECRET_FILE_PATH = "secrets/config.json";
  protected static final String SECRET_FILE_PATH_INSUFFICIENT_ROLES = "secrets/insufficient_roles_config.json";
  protected final S3Format outputFormat;
  protected JsonNode configJson;
  protected GcsDestinationConfig config;
  protected AmazonS3 s3Client;
  protected NamingConventionTransformer nameTransformer;
  protected S3StorageOperations s3StorageOperations;

  public GcsDestinationAcceptanceTest(final S3Format outputFormat) {
    this.outputFormat = outputFormat;
  }

  protected JsonNode getBaseConfigJson() {
    return Jsons.deserialize(IOs.readFile(Path.of(SECRET_FILE_PATH)));
  }

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-gcs:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.has("gcs_bucket_path")) {
      return config.get("gcs_bucket_path").asText();
    }
    return null;
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode baseJson = getBaseConfigJson();
    final JsonNode failCheckJson = Jsons.clone(baseJson);
    // invalid credential
    ((ObjectNode) failCheckJson).put("hmac_key_access_id", "fake-key");
    ((ObjectNode) failCheckJson).put("hmac_key_secret", "fake-secret");
    return failCheckJson;
  }

  /**
   * Helper method to retrieve all synced objects inside the configured bucket path.
   */
  protected List<S3ObjectSummary> getAllSyncedObjects(final String streamName, final String namespace) {
    final String namespaceStr = nameTransformer.getNamespace(namespace);
    final String streamNameStr = nameTransformer.getIdentifier(streamName);
    final String outputPrefix = s3StorageOperations.getBucketObjectPath(
        namespaceStr,
        streamNameStr,
        DateTime.now(DateTimeZone.UTC),
        config.getPathFormat());
    // the child folder contains a non-deterministic epoch timestamp, so use the parent folder
    final String parentFolder = outputPrefix.substring(0, outputPrefix.lastIndexOf("/") + 1);
    final List<S3ObjectSummary> objectSummaries = s3Client
        .listObjects(config.getBucketName(), parentFolder)
        .getObjectSummaries()
        .stream()
        .filter(o -> o.getKey().contains(streamNameStr + "/"))
        .sorted(Comparator.comparingLong(o -> o.getLastModified().getTime()))
        .collect(Collectors.toList());
    LOGGER.info(
        "All objects: {}",
        objectSummaries.stream().map(o -> String.format("%s/%s", o.getBucketName(), o.getKey())).collect(Collectors.toList()));
    return objectSummaries;
  }

  protected abstract JsonNode getFormatConfig();

  /**
   * This method does the following:
   * <li>Construct the GCS destination config.</li>
   * <li>Construct the GCS client.</li>
   */
  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    final JsonNode baseConfigJson = getBaseConfigJson();
    // Set a random GCS bucket path for each integration test
    final JsonNode configJson = Jsons.clone(baseConfigJson);
    final String testBucketPath = String.format(
        "%s_test_%s",
        outputFormat.name().toLowerCase(Locale.ROOT),
        RandomStringUtils.randomAlphanumeric(5));
    ((ObjectNode) configJson)
        .put("gcs_bucket_path", testBucketPath)
        .set("format", getFormatConfig());
    this.configJson = configJson;
    this.config = GcsDestinationConfig.getGcsDestinationConfig(configJson);
    LOGGER.info("Test full path: {}/{}", config.getBucketName(), config.getBucketPath());

    this.s3Client = config.getS3Client();
    this.nameTransformer = new GcsNameTransformer();
    this.s3StorageOperations = new S3StorageOperations(nameTransformer, s3Client, config);
  }

  /**
   * Remove all the S3 output from the tests.
   */
  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    final List<KeyVersion> keysToDelete = new LinkedList<>();
    final List<S3ObjectSummary> objects = s3Client
        .listObjects(config.getBucketName(), config.getBucketPath())
        .getObjectSummaries();
    for (final S3ObjectSummary object : objects) {
      keysToDelete.add(new KeyVersion(object.getKey()));
    }

    if (keysToDelete.size() > 0) {
      LOGGER.info("Tearing down test bucket path: {}/{}", config.getBucketName(),
          config.getBucketPath());
      // Google Cloud Storage doesn't accept request to delete multiple objects
      for (final KeyVersion keyToDelete : keysToDelete) {
        s3Client.deleteObject(config.getBucketName(), keyToDelete.getKey());
      }
      LOGGER.info("Deleted {} file(s).", keysToDelete.size());
    }
  }

  /**
   * Verify that when given user with no Multipart Upload Roles, that check connection returns a
   * failed response. Assume that the #getInsufficientRolesFailCheckConfig() returns the service
   * account has storage.objects.create permission but not storage.multipartUploads.create.
   */
  @Test
  public void testCheckConnectionInsufficientRoles() throws Exception {
    final JsonNode baseConfigJson = Jsons.deserialize(IOs.readFile(Path.of(
        SECRET_FILE_PATH_INSUFFICIENT_ROLES)));

    // Set a random GCS bucket path for each integration test
    final JsonNode configJson = Jsons.clone(baseConfigJson);
    final String testBucketPath = String.format(
        "%s_test_%s",
        outputFormat.name().toLowerCase(Locale.ROOT),
        RandomStringUtils.randomAlphanumeric(5));
    ((ObjectNode) configJson)
        .put("gcs_bucket_path", testBucketPath)
        .set("format", getFormatConfig());

    assertEquals(Status.FAILED, runCheck(configJson).getStatus());
  }

  @Test
  public void testCheckIncorrectHmacKeyAccessIdCredential() {
    final JsonNode baseJson = getBaseConfigJson();
    final JsonNode credential = Jsons.jsonNode(ImmutableMap.builder()
        .put("credential_type", "HMAC_KEY")
        .put("hmac_key_access_id", "fake-key")
        .put("hmac_key_secret", baseJson.get("credential").get("hmac_key_secret").asText())
        .build());

    ((ObjectNode) baseJson).put("credential", credential);
    ((ObjectNode) baseJson).set("format", getFormatConfig());

    final GcsDestination destination = new GcsDestination();
    final AirbyteConnectionStatus status = destination.check(baseJson);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: SignatureDoesNotMatch;"));
  }

  @Test
  public void testCheckIncorrectHmacKeySecretCredential() {
    final JsonNode baseJson = getBaseConfigJson();
    final JsonNode credential = Jsons.jsonNode(ImmutableMap.builder()
        .put("credential_type", "HMAC_KEY")
        .put("hmac_key_access_id", baseJson.get("credential").get("hmac_key_access_id").asText())
        .put("hmac_key_secret", "fake-secret")
        .build());

    ((ObjectNode) baseJson).put("credential", credential);
    ((ObjectNode) baseJson).set("format", getFormatConfig());

    final GcsDestination destination = new GcsDestination();
    final AirbyteConnectionStatus status = destination.check(baseJson);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: SignatureDoesNotMatch;"));
  }

  @Test
  public void testCheckIncorrectBucketCredential() {
    final JsonNode baseJson = getBaseConfigJson();
    ((ObjectNode) baseJson).put("gcs_bucket_name", "fake_bucket");
    ((ObjectNode) baseJson).set("format", getFormatConfig());

    final GcsDestination destination = new GcsDestination();
    final AirbyteConnectionStatus status = destination.check(baseJson);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: NoSuchKey;"));
  }

}
