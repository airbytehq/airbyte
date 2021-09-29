/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
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
    INSERT,
    COPY_S3
  }

  public RedshiftDestination() {
    super(DestinationType.class, RedshiftDestination::getTypeFromConfig, getTypeToDestination());
  }

  public static DestinationType getTypeFromConfig(JsonNode config) {
    if (isCopy(config)) {
      return DestinationType.COPY_S3;
    } else {
      return DestinationType.INSERT;
    }
  }

  public static Map<DestinationType, Destination> getTypeToDestination() {
    final RedshiftInsertDestination insertDestination = new RedshiftInsertDestination();
    final RedshiftCopyS3Destination copyS3Destination = new RedshiftCopyS3Destination();

    return ImmutableMap.of(
        DestinationType.INSERT, insertDestination,
        DestinationType.COPY_S3, copyS3Destination);
  }

  public static boolean isCopy(JsonNode config) {
    var bucketNode = config.get("s3_bucket_name");
    var regionNode = config.get("s3_bucket_region");
    var accessKeyIdNode = config.get("access_key_id");
    var secretAccessKeyNode = config.get("secret_access_key");

    // Since region is a Json schema enum with an empty string default, we consider the empty string an
    // unset field.
    var emptyRegion = regionNode == null || regionNode.asText().equals("");

    if (bucketNode == null && emptyRegion && accessKeyIdNode == null && secretAccessKeyNode == null) {
      return false;
    }

    if (bucketNode == null || regionNode == null || accessKeyIdNode == null || secretAccessKeyNode == null) {
      throw new RuntimeException("Error: Partially missing S3 Configuration.");
    }
    return true;
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new RedshiftDestination();
    LOGGER.info("starting destination: {}", RedshiftDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", RedshiftDestination.class);
  }

}
