/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
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
    INSERT_WITH_VARCHAR,
    INSERT_WITH_SUPER_TMP_TYPE,
    COPY_S3_WITH_VARCHAR,
    COPY_S3_WITH_SUPER_TMP_TYPE
  }

  public RedshiftDestination() {
    super(DestinationType.class, RedshiftDestination::getTypeFromConfig, getTypeToDestination());
  }

  public static DestinationType getTypeFromConfig(final JsonNode config) {
    return determineUploadMode(config);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog,
      Consumer<AirbyteMessage> outputRecordCollector) throws Exception {
    final DestinationType destinationType = super.configToType.apply(config);
    LOGGER.info("Using destination type: " + destinationType.name());
    return typeToDestination.get(destinationType).getConsumer(config, catalog, outputRecordCollector);
  }

  public static Map<DestinationType, Destination> getTypeToDestination() {
    final RedshiftInsertDestination insertDestinationWithVarcharTmp = new RedshiftInsertDestination(RedshiftDataTmpTableMode.VARCHAR);
    final RedshiftInsertDestination insertDestinationWithSuperTmp = new RedshiftInsertDestination(RedshiftDataTmpTableMode.SUPER);
    final RedshiftCopyS3Destination copyS3DestinationWithVarcharTmp = new RedshiftCopyS3Destination(RedshiftDataTmpTableMode.VARCHAR);
    final RedshiftCopyS3Destination copyS3DestinationWithSuperTmp = new RedshiftCopyS3Destination(RedshiftDataTmpTableMode.SUPER);
    return Map.of(
        DestinationType.INSERT_WITH_VARCHAR, insertDestinationWithVarcharTmp,
        DestinationType.INSERT_WITH_SUPER_TMP_TYPE, insertDestinationWithSuperTmp,
        DestinationType.COPY_S3_WITH_VARCHAR, copyS3DestinationWithVarcharTmp,
        DestinationType.COPY_S3_WITH_SUPER_TMP_TYPE, copyS3DestinationWithSuperTmp);
  }

  public static DestinationType determineUploadMode(final JsonNode config) {
    final var bucketNode = config.get("s3_bucket_name");
    final var regionNode = config.get("s3_bucket_region");
    final var accessKeyIdNode = config.get("access_key_id");
    final var secretAccessKeyNode = config.get("secret_access_key");

    // Since region is a Json schema enum with an empty string default, we consider the empty string an
    // unset field.
    final var emptyRegion = regionNode == null || regionNode.asText().equals("");

    if (bucketNode == null && emptyRegion && accessKeyIdNode == null && secretAccessKeyNode == null) {
      return determineTmpTableDatatype(config) == RedshiftDataTmpTableMode.VARCHAR ?
          DestinationType.INSERT_WITH_VARCHAR :
          DestinationType.INSERT_WITH_SUPER_TMP_TYPE;
    }

    if (bucketNode == null || regionNode == null || accessKeyIdNode == null || secretAccessKeyNode == null) {
      throw new RuntimeException("Error: Partially missing S3 Configuration.");
    }
    return determineTmpTableDatatype(config) == RedshiftDataTmpTableMode.VARCHAR ?
        DestinationType.COPY_S3_WITH_VARCHAR :
        DestinationType.COPY_S3_WITH_SUPER_TMP_TYPE;
  }

  private static RedshiftDataTmpTableMode determineTmpTableDatatype(JsonNode config) {
    if (config.get("use_super_redshift_type") != null && !config.get("use_super_redshift_type").isNull() && config.get("use_super_redshift_type").asBoolean()) {
      return RedshiftDataTmpTableMode.SUPER;
    }
    return RedshiftDataTmpTableMode.VARCHAR;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new RedshiftDestination();
    LOGGER.info("starting destination: {}", RedshiftDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", RedshiftDestination.class);
  }

}
