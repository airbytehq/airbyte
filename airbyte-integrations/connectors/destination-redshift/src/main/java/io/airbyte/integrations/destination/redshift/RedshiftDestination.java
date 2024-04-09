/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.integrations.destination.redshift.util.RedshiftUtil.anyOfS3FieldsAreNullOrEmpty;
import static io.airbyte.integrations.destination.redshift.util.RedshiftUtil.findS3Options;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.destination.jdbc.copy.SwitchingDestination;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
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

  enum DestinationType {
    STANDARD,
    COPY_S3
  }

  private static final Map<DestinationType, Destination> destinationMap = Map.of(
      DestinationType.STANDARD, RedshiftInsertDestination.sshWrappedDestination(),
      DestinationType.COPY_S3, RedshiftStagingS3Destination.sshWrappedDestination());

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

  @Override
  public ConnectorSpecification spec() throws Exception {
    // inject the standard ssh configuration into the spec.
    final ConnectorSpecification originalSpec = super.spec();
    final ObjectNode propNode = (ObjectNode) originalSpec.getConnectionSpecification().get("properties");
    propNode.set("tunnel_method", Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json")));
    return originalSpec;
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new RedshiftDestination();
    LOGGER.info("starting destination: {}", RedshiftDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", RedshiftDestination.class);
  }

}
