/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.destination.bigquery.DestinationBigqueryConnectionConfig.DatasetLocation;
import io.airbyte.integrations.destination.bigquery.DestinationBigqueryConnectionConfig.TransformationPriority;
import io.airbyte.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

public class BigQueryExecutionConfigTest {

  @MethodSource("configSpecProvider")
  @ParameterizedTest
  public void connSpecDeserTest(String configFilePath, Consumer<BigQueryExecutionConfig> assertionConsumer) throws Exception {

    final String tmpConfigAsString = MoreResources.readResource(configFilePath);
    final ObjectNode config = (ObjectNode) Jsons.deserialize(tmpConfigAsString);
    config.put(BigQueryConsts.CONFIG_DATASET_ID, "dummy_dataset");
    assertionConsumer.accept(BigQueryUtils.createExecutionConfig(config));
  }

  public static Stream<Arguments> configSpecProvider() {
    final Consumer<BigQueryExecutionConfig> gcsConfigVerifier = config -> {
      verifyAllFields(config);
      assertEquals(UploadingMethod.GCS, config.getUploadingMethod());
      assertTrue(config.getDestinationConfig().isPresent());
      assertEquals("airbyte-integration-test-destination-gcs", config.getDestinationConfig().get().getBucketName());
      assertEquals("test_path", config.getDestinationConfig().get().getBucketPath());
      assertEquals("us-west1", config.getDestinationConfig().get().getBucketRegion());
      assertTrue(config.getDestinationConfig().get().getGcsCredentialConfig() instanceof GcsHmacKeyCredentialConfig);
      GcsHmacKeyCredentialConfig credentialConfig = ((GcsHmacKeyCredentialConfig) config.getDestinationConfig().get().getGcsCredentialConfig());
      assertEquals("GOOGDEADBEEF11110000", credentialConfig.getHmacKeyAccessId());
      assertEquals("Garbagev012asdfas", credentialConfig.getHmacKeySecret());
      assertEquals("HMAC_KEY", credentialConfig.getCredentialType().name());
    };
    final Consumer<BigQueryExecutionConfig> standardConfigVerifier = config -> {
      verifyAllFields(config);
      assertEquals(UploadingMethod.STANDARD, config.getUploadingMethod());
    };
    final Consumer<BigQueryExecutionConfig> requiredMissingVerified = config -> {
      assertEquals(UploadingMethod.STANDARD, config.getUploadingMethod());
      assertNull(config.getConnectionConfig().getDatasetLocation());
      assertNull(config.getConnectionConfig().getProjectId());
    };
    // At somepoint credentials_json was an object. Preserve backward compatibility for config
    // migrations
    final Consumer<BigQueryExecutionConfig> credsOldStyleConfig = config -> {
      assertNotNull(config.getConnectionConfig().getCredentialsJson());
      assertFalse(config.getConnectionConfig().getCredentialsJson().isEmpty());
      assertFalse(config.getConnectionConfig().getCredentialsJson().isBlank());
    };
    return Stream.of(Arguments.arguments("connection-spec/gcs.json", gcsConfigVerifier),
        Arguments.arguments("connection-spec/standard.json", standardConfigVerifier),
        Arguments.arguments("connection-spec/standard-missing-required.json", requiredMissingVerified),
        Arguments.arguments("connection-spec/gcs-credentials-object.json", credsOldStyleConfig));
  }

  public static void verifyAllFields(BigQueryExecutionConfig config) {
    assertNotNull(config.getUploadingMethod());
    assertNotNull(config.getConnectionConfig().getDatasetLocation());
    assertNotNull(config.getConnectionConfig().getCredentialsJson());
    assertEquals("dummy_dataset", config.getConnectionConfig().getDatasetId());
    assertEquals("dataline-integration-testing", config.getConnectionConfig().getProjectId());
    assertEquals(TransformationPriority.INTERACTIVE, config.getConnectionConfig().getTransformationPriority());
    assertEquals(DatasetLocation.US, config.getConnectionConfig().getDatasetLocation());
    assertFalse(config.getConnectionConfig().getCredentialsJson().isEmpty());
    assertEquals(15, config.getConnectionConfig().getBigQueryClientBufferSizeMb());

    // Test unknown properties to be preserved during config migration phases.
    assertEquals("data", config.getConnectionConfig().getAdditionalProperties().get("unknown_property_from_spec").asText());
  }

}
