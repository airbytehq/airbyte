/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.integrations.destination.redshift.util.RedshiftUtil.anyOfS3FieldsAreNullOrEmpty;
import static io.airbyte.integrations.destination.redshift.util.RedshiftUtil.findS3Options;

import com.fasterxml.jackson.databind.JsonNode;
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
 * credentials. See {@link RedshiftStagingS3Destination} for more detail. This class inspect the
 * given arguments to determine which strategy to use.
 */
public class RedshiftDestination extends SwitchingDestination<RedshiftDestination.DestinationType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftDestination.class);
  private static final String METHOD = "method";

  private static final Map<DestinationType, Destination> destinationMap = Map.of(
      DestinationType.STANDARD, new RedshiftInsertDestination(),
      DestinationType.COPY_S3, new RedshiftStagingS3Destination());

  enum DestinationType {
    STANDARD,
    COPY_S3
  }

  public RedshiftDestination() {
    super(DestinationType.class, RedshiftDestination::getTypeFromConfig, destinationMap);
  }

  private static DestinationType getTypeFromConfig(final JsonNode config) {
    return determineUploadMode(config);
  }

  public static DestinationType determineUploadMode(final JsonNode config) {

    final JsonNode jsonNode = findS3Options(config);

    if (anyOfS3FieldsAreNullOrEmpty(jsonNode)) {
      LOGGER.warn("The \"standard\" upload mode is not performant, and is not recommended for production. " +
          "Please use the Amazon S3 upload mode if you are syncing a large amount of data.");
      return DestinationType.STANDARD;
    }
    return DestinationType.COPY_S3;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new RedshiftDestination();
    LOGGER.info("starting destination: {}", RedshiftDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", RedshiftDestination.class);
  }

}
