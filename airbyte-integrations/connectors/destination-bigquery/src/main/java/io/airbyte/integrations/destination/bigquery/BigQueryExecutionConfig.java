/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.destination.s3.S3FormatConfig;
import io.airbyte.cdk.integrations.destination.s3.S3FormatConfigs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfig;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialType;
import io.airbyte.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig;
import java.util.Map;
import java.util.Optional;
import lombok.Getter;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;

@Getter
@ToString
@Slf4j
public class BigQueryExecutionConfig {

  private final DestinationBigqueryConnectionConfig connectionConfig;

  private final UploadingMethod uploadingMethod;

  private Optional<GcsDestinationConfig> destinationConfig;

  private final boolean keepFilesInGcs;

  BigQueryExecutionConfig(final DestinationBigqueryConnectionConfig connectionConfig,
                          final Optional<GcsDestinationConfig> destinationConfig,
                          final UploadingMethod uploadingMethod,
                          final boolean keepFilesInGcs) {
    this.connectionConfig = connectionConfig;
    this.destinationConfig = destinationConfig;
    this.uploadingMethod = uploadingMethod;
    this.keepFilesInGcs = keepFilesInGcs;
  }

  public static BigQueryExecutionConfigBuilder builder() {
    return new BigQueryExecutionConfigBuilder();
  }

  public static class BigQueryExecutionConfigBuilder {

    private static final String GCS_STAGING = "GCS Staging";
    private static final String S3_FORMAT_TYPE_KEY = "format_type";
    private static final String S3_FORMAT_TYPE_VALUE = "CSV";
    private static final String S3_FLATTENING_KEY = "flattening";
    private static final String S3_FLATTENING_VALUE = "No flattening";

    private DestinationBigqueryConnectionConfig connectionConfig;

    public BigQueryExecutionConfigBuilder connectionConfig(final DestinationBigqueryConnectionConfig connectionConfig) {
      this.connectionConfig = connectionConfig;
      return this;
    }

    public BigQueryExecutionConfig build() {
      final UploadingMethod uploadingMethod =
          connectionConfig.getLoadingMethod().getMethod().equals(GCS_STAGING) ? UploadingMethod.GCS : UploadingMethod.STANDARD;
      final Optional<GcsDestinationConfig> destinationConfig;
      final boolean keepFilesInGcs;
      if (uploadingMethod == UploadingMethod.GCS) {
        final Map<String, JsonNode> gcsProperties = connectionConfig.getLoadingMethod().getAdditionalProperties();
        final String gcsBucketName = gcsProperties.get(BigQueryConsts.GCS_BUCKET_NAME).asText();
        final String gcsBucketPath = gcsProperties.get(BigQueryConsts.GCS_BUCKET_PATH).asText();
        final String gcsBucketRegion = gcsProperties.get(BigQueryConsts.GCS_BUCKET_REGION).asText();
        // This can be inlined but intentionally split to keep log statements intact for debugging
        if (gcsProperties.get(BigQueryConsts.KEEP_GCS_FILES) != null && BigQueryConsts.KEEP_GCS_FILES_VAL.equals(
            gcsProperties.get(BigQueryConsts.KEEP_GCS_FILES).asText())) {
          keepFilesInGcs = true;
          log.info("All tmp files GCS will be kept in bucket when replication is finished");

        } else {
          keepFilesInGcs = false;
          log.info("All tmp files will be removed from GCS when replication is finished");
        }
        // Lot of assumptions of the type of JsonNode.
        final JsonNode credentialConfig = gcsProperties.get(BigQueryConsts.CREDENTIAL);
        // TODO: Move this logic to GcsCredentialConfigs, right now it expects a key credential inside
        // JsonNode.
        if (!credentialConfig.isObject()) {
          throw new RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig));
        }
        final GcsCredentialType credentialType =
            GcsCredentialType.valueOf(credentialConfig.get(BigQueryConsts.CREDENTIAL_TYPE).asText().toUpperCase());

        if (credentialType != GcsCredentialType.HMAC_KEY) {
          throw new RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig));
        }
        // Reusing existing formatConfig factory
        final S3FormatConfig s3FormatConfig = S3FormatConfigs.getS3FormatConfig(
            Jsons.jsonNode(ImmutableMap.builder().put(BigQueryConsts.FORMAT, ImmutableMap.builder()
                .put(S3_FORMAT_TYPE_KEY, S3_FORMAT_TYPE_VALUE)
                .put(S3_FLATTENING_KEY, S3_FLATTENING_VALUE)
                .build()).build()));
        final GcsCredentialConfig gcsCredentialConfig = new GcsHmacKeyCredentialConfig(credentialConfig);

        destinationConfig = Optional.of(new GcsDestinationConfig(gcsBucketName, gcsBucketPath, gcsBucketRegion, gcsCredentialConfig, s3FormatConfig));
      } else {
        destinationConfig = Optional.empty();
        keepFilesInGcs = false;
      }
      return new BigQueryExecutionConfig(this.connectionConfig, destinationConfig, uploadingMethod, keepFilesInGcs);
    }

  }

}
