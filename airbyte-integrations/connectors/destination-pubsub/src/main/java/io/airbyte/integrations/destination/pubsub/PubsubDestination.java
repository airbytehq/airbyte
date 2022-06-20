/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pubsub;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.pubsub.v1.TopicAdminClient;
import com.google.cloud.pubsub.v1.TopicAdminSettings;
import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import com.google.iam.v1.TestIamPermissionsRequest;
import com.google.iam.v1.TestIamPermissionsResponse;
import com.google.pubsub.v1.TopicName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.ByteArrayInputStream;
import java.util.List;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PubsubDestination extends BaseConnector implements Destination {

  static final String CONFIG_TOPIC_ID = "topic_id";
  static final String CONFIG_PROJECT_ID = "project_id";
  static final String CONFIG_CREDS = "credentials_json";
  static final String STREAM = "_stream";
  static final String NAMESPACE = "_namespace";
  private static final Logger LOGGER = LoggerFactory.getLogger(PubsubDestination.class);

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new PubsubDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final String projectId = config.get(CONFIG_PROJECT_ID).asText();
      final String topicId = config.get(CONFIG_TOPIC_ID).asText();
      final String credentialsString =
          config.get(CONFIG_CREDS).isObject() ? Jsons.serialize(config.get(CONFIG_CREDS))
              : config.get(CONFIG_CREDS).asText();
      final ServiceAccountCredentials credentials = ServiceAccountCredentials
          .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));

      final TopicAdminClient adminClient = TopicAdminClient
          .create(TopicAdminSettings.newBuilder().setCredentialsProvider(
              FixedCredentialsProvider.create(credentials)).build());

      // check if topic is present and the service account has necessary permissions on it
      final TopicName topicName = TopicName.of(projectId, topicId);
      final List<String> requiredPermissions = List.of("pubsub.topics.publish");
      final TestIamPermissionsResponse response = adminClient.testIamPermissions(
          TestIamPermissionsRequest.newBuilder().setResource(topicName.toString())
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
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return new PubsubConsumer(config, configuredCatalog, outputRecordCollector);
  }

}
