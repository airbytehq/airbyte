/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pubsub;

import static com.google.common.base.Strings.nullToEmpty;
import static io.airbyte.integrations.destination.pubsub.PubsubDestination.NAMESPACE;
import static io.airbyte.integrations.destination.pubsub.PubsubDestination.STREAM;
import static io.airbyte.integrations.destination.pubsub.PubsubDestinationConfig.CONFIG_BATCHING_ENABLED;
import static io.airbyte.integrations.destination.pubsub.PubsubDestinationConfig.CONFIG_CREDS;
import static io.airbyte.integrations.destination.pubsub.PubsubDestinationConfig.CONFIG_ORDERING_ENABLED;
import static io.airbyte.integrations.destination.pubsub.PubsubDestinationConfig.CONFIG_PROJECT_ID;
import static io.airbyte.integrations.destination.pubsub.PubsubDestinationConfig.CONFIG_TOPIC_ID;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.Lists;
import com.google.api.gax.core.FixedCredentialsProvider;
import com.google.auth.Credentials;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.pubsub.v1.SubscriptionAdminClient;
import com.google.cloud.pubsub.v1.SubscriptionAdminSettings;
import com.google.cloud.pubsub.v1.TopicAdminClient;
import com.google.cloud.pubsub.v1.TopicAdminSettings;
import com.google.cloud.pubsub.v1.stub.GrpcSubscriberStub;
import com.google.cloud.pubsub.v1.stub.SubscriberStub;
import com.google.cloud.pubsub.v1.stub.SubscriberStubSettings;
import com.google.common.collect.ImmutableMap;
import com.google.pubsub.v1.AcknowledgeRequest;
import com.google.pubsub.v1.ProjectSubscriptionName;
import com.google.pubsub.v1.PullRequest;
import com.google.pubsub.v1.PullResponse;
import com.google.pubsub.v1.ReceivedMessage;
import com.google.pubsub.v1.Subscription;
import com.google.pubsub.v1.Topic;
import com.google.pubsub.v1.TopicName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PubsubDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory
      .getLogger(PubsubDestinationAcceptanceTest.class);
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private TopicAdminClient topicAdminClient;
  private SubscriptionAdminClient subscriptionAdminClient;
  private TopicName topicName;
  private ProjectSubscriptionName subscriptionName;
  private Credentials credentials;
  private JsonNode configJson;
  // Store retrieved data during the test run since we can't re-read it multiple times (ACKing
  // messages causes them to be removed from pubsub)
  private List<JsonNode> records;

  @Override
  protected String getImageName() {
    return "airbyte/destination-pubsub:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    ((ObjectNode) configJson).put(CONFIG_PROJECT_ID, "fake");
    return configJson;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  private AirbyteStreamNameNamespacePair fromJsonNode(final JsonNode j) {
    final var stream = j.get(STREAM).asText("");
    final var namespace = j.get(NAMESPACE).asText("");
    return new AirbyteStreamNameNamespacePair(stream, namespace);
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws IOException {
    if (records.isEmpty()) {
      // first time retrieving records, retrieve all and keep locally for easier
      // verification
      final SubscriberStubSettings subscriberStubSettings =
          SubscriberStubSettings.newBuilder()
              .setCredentialsProvider(FixedCredentialsProvider.create(credentials))
              .setTransportChannelProvider(
                  SubscriberStubSettings.defaultGrpcTransportProviderBuilder()
                      .setCredentials(credentials)
                      .build())
              .build();
      try (final SubscriberStub subscriber = GrpcSubscriberStub.create(subscriberStubSettings)) {
        final PullRequest pullRequest =
            PullRequest.newBuilder()
                .setMaxMessages(1000)
                .setSubscription(subscriptionName.toString())
                .build();

        PullResponse pullResponse = subscriber.pullCallable()
            .call(pullRequest);
        var list = pullResponse.getReceivedMessagesList();
        do {
          final List<String> ackIds = Lists.newArrayList();
          for (final ReceivedMessage message : list) {
            final var m = message.getMessage();
            final var s = m.getAttributesMap().get(STREAM);
            final var n = m.getAttributesMap().get(NAMESPACE);
            records.add(Jsons.jsonNode(ImmutableMap.of(
                STREAM, nullToEmpty(s),
                NAMESPACE, nullToEmpty(n),
                "data", Jsons.deserialize(m.getData().toStringUtf8())
                    .get(JavaBaseConstants.COLUMN_NAME_DATA))));
            ackIds.add(message.getAckId());
          }
          if (!ackIds.isEmpty()) {
            // Acknowledge received messages.
            final AcknowledgeRequest acknowledgeRequest =
                AcknowledgeRequest.newBuilder()
                    .setSubscription(subscriptionName.toString())
                    .addAllAckIds(ackIds)
                    .build();
            // Use acknowledgeCallable().futureCall to asynchronously perform this operation.
            subscriber.acknowledgeCallable().call(acknowledgeRequest);
          }
          pullResponse = subscriber.pullCallable()
              .call(pullRequest);
          list = pullResponse.getReceivedMessagesList();
        } while (list.size() > 0);
      }
    }

    // at this point we have fetched all records first time, or it was already there
    // just filter based on stream/ns and send results back
    return records
        .stream()
        .filter(Objects::nonNull)
        .filter(
            e -> fromJsonNode(e).equals(new AirbyteStreamNameNamespacePair(nullToEmpty(streamName),
                nullToEmpty(namespace))))
        .map(e -> e.get("data"))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a gcp service account credentials file. By default {module-root}/"
              + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);

    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
    final String topicId = Strings.addRandomSuffix("airbyte_tests", "_", 8);
    final String subscriptionId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    configJson = Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(CONFIG_CREDS, credentialsJsonString)
        .put(CONFIG_TOPIC_ID, topicId)
        .put(CONFIG_BATCHING_ENABLED, true)
        .put(CONFIG_ORDERING_ENABLED, true)
        .build());

    credentials =
        ServiceAccountCredentials
            .fromStream(new ByteArrayInputStream(configJson.get(CONFIG_CREDS).asText().getBytes(
                StandardCharsets.UTF_8)));
    // create topic
    topicName = TopicName.of(projectId, topicId);
    topicAdminClient = TopicAdminClient
        .create(TopicAdminSettings.newBuilder().setCredentialsProvider(
            FixedCredentialsProvider.create(credentials)).build());
    final Topic topic = topicAdminClient.createTopic(topicName);
    LOGGER.info("Created topic: " + topic.getName());

    // create subscription - with ordering, cause tests expect it
    subscriptionName = ProjectSubscriptionName.of(projectId, subscriptionId);
    subscriptionAdminClient = SubscriptionAdminClient.create(
        SubscriptionAdminSettings.newBuilder()
            .setCredentialsProvider(FixedCredentialsProvider.create(credentials))
            .build());
    final Subscription subscription =
        subscriptionAdminClient.createSubscription(
            Subscription.newBuilder().setName(subscriptionName.toString())
                .setTopic(topicName.toString()).setEnableMessageOrdering(true)
                .setAckDeadlineSeconds(10).build());
    LOGGER.info("Created pull subscription: " + subscription.getName());

    // init local records container
    records = Lists.newArrayList();
  }

  @Override
  public void testSecondSync() throws Exception {
    // PubSub cannot overwrite messages, its always append only
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    // delete subscription
    if (subscriptionAdminClient != null && subscriptionName != null) {
      subscriptionAdminClient.deleteSubscription(subscriptionName);
      subscriptionAdminClient.close();
    }
    // delete topic
    if (topicAdminClient != null && topicName != null) {
      topicAdminClient.deleteTopic(topicName);
      topicAdminClient.close();
    }
    records.clear();
  }

}
