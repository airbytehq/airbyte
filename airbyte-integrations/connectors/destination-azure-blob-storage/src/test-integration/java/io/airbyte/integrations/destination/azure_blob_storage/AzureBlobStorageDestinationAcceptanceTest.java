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

package io.airbyte.integrations.destination.azure_blob_storage;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AzureBlobStorageDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected static final Logger LOGGER = LoggerFactory
      .getLogger(AzureBlobStorageDestinationAcceptanceTest.class);
  protected static final ObjectMapper MAPPER = MoreMappers.initMapper();

  protected final String secretFilePath = "secrets/config.json";
  protected final AzureBlobStorageFormat outputFormat;
  protected JsonNode configJson;
  protected AzureBlobStorageDestinationConfig config;

  protected AzureBlobStorageDestinationAcceptanceTest(AzureBlobStorageFormat outputFormat) {
    this.outputFormat = outputFormat;
  }

  protected JsonNode getBaseConfigJson() {
    return Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)));
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-azure-blob-storage:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "invalidAccountName")
        .put("azure_blob_storage_account_key", "invalidAccountKey")
        .put("azure_blob_storage_endpoint_domain_name", "InvalidDomainName")
        .put("format", getFormatConfig())
        .build());
  }

  // /**
  // * Helper method to retrieve all synced objects inside the configured bucket path.
  // */
  // protected List<S3ObjectSummary> getAllSyncedObjects(String streamName, String namespace) {
  // String outputPrefix = S3OutputPathHelper
  // .getOutputPrefix(config.getBucketPath(), namespace, streamName);
  // List<S3ObjectSummary> objectSummaries = s3Client
  // .listObjects(config.getBucketName(), outputPrefix)
  // .getObjectSummaries()
  // .stream()
  // .sorted(Comparator.comparingLong(o -> o.getLastModified().getTime()))
  // .collect(Collectors.toList());
  // LOGGER.info(
  // "All objects: {}",
  // objectSummaries.stream().map(o -> String.format("%s/%s", o.getBucketName(),
  // o.getKey())).collect(Collectors.toList()));
  // return objectSummaries;
  // }

  protected abstract JsonNode getFormatConfig();

  /**
   * This method does the following:
   * <li>Construct the S3 destination config.</li>
   * <li>Construct the S3 client.</li>
   */
  @Override
  protected void setup(TestDestinationEnv testEnv) {
    JsonNode baseConfigJson = getBaseConfigJson();

    configJson = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name",
            baseConfigJson.get("azure_blob_storage_account_name"))
        .put("azure_blob_storage_account_key", baseConfigJson.get("azure_blob_storage_account_key"))
        .put("azure_blob_storage_endpoint_domain_name",
            baseConfigJson.get("azure_blob_storage_endpoint_domain_name"))
        .put("azure_blob_storage_container_name",
            baseConfigJson.get("azure_blob_storage_container_name"))
        .put("azure_blob_storage_blob_name",
            baseConfigJson.get("azure_blob_storage_blob_name"))
        .put("format", getFormatConfig())
        .build());
    // // Set a random s3 bucket path for each integration test
    // JsonNode configJson = Jsons.clone(baseConfigJson);
    // String testBucketPath = String.format(
    // "%s_test_%s",
    // outputFormat.name().toLowerCase(Locale.ROOT),
    // RandomStringUtils.randomAlphanumeric(5));
    // ((ObjectNode) configJson)
    // .put("s3_bucket_path", testBucketPath)
    // .set("format", getFormatConfig());
    // this.configJson = configJson;
    // this.config = S3DestinationConfig.getS3DestinationConfig(configJson);
    // LOGGER.info("Test full path: {}/{}", config.getBucketName(), config.getBucketPath());
    //
    // AWSCredentials awsCreds = new BasicAWSCredentials(config.getAccessKeyId(),
    // config.getSecretAccessKey());
    // String endpoint = config.getEndpoint();
    //
    // if (endpoint.isEmpty()) {
    // this.s3Client = AmazonS3ClientBuilder.standard()
    // .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
    // .withRegion(config.getBucketRegion())
    // .build();
    // } else {
    // ClientConfiguration clientConfiguration = new ClientConfiguration();
    // clientConfiguration.setSignerOverride("AWSS3V4SignerType");
    //
    // this.s3Client = AmazonS3ClientBuilder
    // .standard()
    // .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint,
    // config.getBucketRegion()))
    // .withPathStyleAccessEnabled(true)
    // .withClientConfiguration(clientConfiguration)
    // .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
    // .build();
    // }
  }

  /**
   * Remove all the S3 output from the tests.
   */
  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // List<KeyVersion> keysToDelete = new LinkedList<>();
    // List<S3ObjectSummary> objects = s3Client
    // .listObjects(config.getBucketName(), config.getBucketPath())
    // .getObjectSummaries();
    // for (S3ObjectSummary object : objects) {
    // keysToDelete.add(new KeyVersion(object.getKey()));
    // }
    //
    // if (keysToDelete.size() > 0) {
    // LOGGER.info("Tearing down test bucket path: {}/{}", config.getBucketName(),
    // config.getBucketPath());
    // DeleteObjectsResult result = s3Client
    // .deleteObjects(new DeleteObjectsRequest(config.getBucketName()).withKeys(keysToDelete));
    // LOGGER.info("Deleted {} file(s).", result.getDeletedObjects().size());
    // }
  }

}
