/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pubsub;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.cloud.pubsub.v1.TopicAdminClient;
import com.google.cloud.pubsub.v1.TopicAdminSettings;
import com.google.common.base.Preconditions;
import com.google.iam.v1.TestIamPermissionsRequest;
import com.google.iam.v1.TestIamPermissionsResponse;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.List;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PubsubDestination extends BaseConnector implements Destination {

  static final String STREAM = "_stream";
  static final String NAMESPACE = "_namespace";
  private static final Logger LOGGER = LoggerFactory.getLogger(PubsubDestination.class);

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new PubsubDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      var pubsubDestinationConfig = PubsubDestinationConfig.fromJsonNode(config);
      final TopicAdminClient adminClient = TopicAdminClient
          .create(TopicAdminSettings.newBuilder().setCredentialsProvider(
              FixedCredentialsProvider.create(pubsubDestinationConfig.getCredentials())).build());

      // check if topic is present and the service account has necessary permissions on it
      final List<String> requiredPermissions = List.of("pubsub.topics.publish");
      final TestIamPermissionsResponse response = adminClient.testIamPermissions(
          TestIamPermissionsRequest.newBuilder().setResource(pubsubDestinationConfig.getTopic().toString())
              .addAllPermissions(requiredPermissions).build());
      Preconditions.checkArgument(response.getPermissionsList().containsAll(requiredPermissions),
          "missing required permissions " + requiredPermissions);

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.info("Check failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED)
          .withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws IOException {
    return new PubsubConsumer(PubsubDestinationConfig.fromJsonNode(config), configuredCatalog, outputRecordCollector);
  }

}
