/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The Redshift Destination offers two replication strategies. The first inserts via a typical SQL
 * Insert statement. Although less efficient, this requires less user set up. See
 * {@link RedshiftInsertDestination} for more detail. The second inserts via streaming the data to
 * an S3 bucket, and Cop-ing the date into Redshift. This is more efficient, and recommended for
 * production workloads, but does require users to set up an S3 bucket and pass in additional
 * credentials. See {@link RedshiftCopyS3Destination} for more detail. This class inspect the given
 * arguments to determine which strategy to use.
 */
public class RedshiftDestination extends SwitchingDestination<RedshiftDestination.DestinationType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftDestination.class);

  enum DestinationType {
    INSERT_WITH_SUPER_TMP_TYPE,
    COPY_S3_WITH_SUPER_TMP_TYPE
  }

  public RedshiftDestination() {
    super(DestinationType.class, RedshiftDestination::getTypeFromConfig, getTypeToDestination());
  }

  public static DestinationType getTypeFromConfig(final JsonNode config) {
    return determineUploadMode(config);
  }

  public static Map<DestinationType, Destination> getTypeToDestination() {
    return Map.of(
        DestinationType.INSERT_WITH_SUPER_TMP_TYPE, new RedshiftInsertDestination(RedshiftDataTmpTableMode.SUPER),
        DestinationType.COPY_S3_WITH_SUPER_TMP_TYPE, new RedshiftCopyS3Destination(RedshiftDataTmpTableMode.SUPER));
  }

  public static DestinationType determineUploadMode(final JsonNode config) {
    final var bucketNode = config.get("s3_bucket_name");
    final var regionNode = config.get("s3_bucket_region");
    final var accessKeyIdNode = config.get("access_key_id");
    final var secretAccessKeyNode = config.get("secret_access_key");

    if (isNullOrEmpty(bucketNode) && isNullOrEmpty(regionNode) && isNullOrEmpty(accessKeyIdNode)
        && isNullOrEmpty(secretAccessKeyNode)) {
      LOGGER.warn("The \"standard\" upload mode is not performant, and is not recommended for production. " +
          "Please use the Amazon S3 upload mode if you are syncing a large amount of data.");
      return DestinationType.INSERT_WITH_SUPER_TMP_TYPE;
    }

    if (isNullOrEmpty(bucketNode) && isNullOrEmpty(regionNode) && isNullOrEmpty(accessKeyIdNode)
        && isNullOrEmpty(secretAccessKeyNode)) {
      throw new RuntimeException("Error: Partially missing S3 Configuration.");
    }
    return DestinationType.COPY_S3_WITH_SUPER_TMP_TYPE;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new RedshiftDestination();
    LOGGER.info("starting destination: {}", RedshiftDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", RedshiftDestination.class);
  }

  private static boolean isNullOrEmpty(JsonNode jsonNode) {
    return jsonNode == null || jsonNode.asText().equals("");
  }

}
