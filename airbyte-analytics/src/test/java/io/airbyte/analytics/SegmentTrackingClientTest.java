/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import com.segment.analytics.Analytics;
import com.segment.analytics.messages.IdentifyMessage;
import com.segment.analytics.messages.TrackMessage;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class SegmentTrackingClientTest {

  private static final AirbyteVersion AIRBYTE_VERSION = new AirbyteVersion("dev");
  private static final Deployment DEPLOYMENT = new Deployment(Configs.DeploymentMode.OSS, UUID.randomUUID(), WorkerEnvironment.DOCKER);
  private static final String EMAIL = "a@airbyte.io";
  private static final TrackingIdentity IDENTITY = new TrackingIdentity(AIRBYTE_VERSION, UUID.randomUUID(), EMAIL, false, false, true);
  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final Function<UUID, TrackingIdentity> MOCK_TRACKING_IDENTITY = (workspaceId) -> IDENTITY;
  private static final String AIRBYTE_VERSION_KEY = "airbyte_version";
  private static final String JUMP = "jump";

  private Analytics analytics;
  private SegmentTrackingClient segmentTrackingClient;
  private Supplier<String> roleSupplier;

  @BeforeEach
  @SuppressWarnings("unchecked")
  void setup() {
    analytics = mock(Analytics.class);
    roleSupplier = mock(Supplier.class);
    segmentTrackingClient = new SegmentTrackingClient(MOCK_TRACKING_IDENTITY, DEPLOYMENT, null, analytics);
  }

  @SuppressWarnings("OptionalGetWithoutIsPresent")
  @Test
  void testIdentify() {
    // equals is not defined on MessageBuilder, so we need to use ArgumentCaptor to inspect each field
    // manually.
    final ArgumentCaptor<IdentifyMessage.Builder> mockBuilder = ArgumentCaptor.forClass(IdentifyMessage.Builder.class);

    segmentTrackingClient.identify(WORKSPACE_ID);

    verify(analytics).enqueue(mockBuilder.capture());
    final IdentifyMessage actual = mockBuilder.getValue().build();
    final Map<String, Object> expectedTraits = ImmutableMap.<String, Object>builder()
        .put("anonymized", IDENTITY.isAnonymousDataCollection())
        .put(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION.serialize())
        .put("deployment_env", DEPLOYMENT.getDeploymentEnv())
        .put("deployment_mode", DEPLOYMENT.getDeploymentMode())
        .put("deployment_id", DEPLOYMENT.getDeploymentId())
        .put("email", IDENTITY.getEmail().get())
        .put("subscribed_newsletter", IDENTITY.isNews())
        .put("subscribed_security", IDENTITY.isSecurityUpdates())
        .build();
    assertEquals(IDENTITY.getCustomerId().toString(), actual.userId());
    assertEquals(expectedTraits, actual.traits());
  }

  @Test
  void testIdentifyWithRole() {
    segmentTrackingClient = new SegmentTrackingClient((workspaceId) -> IDENTITY, DEPLOYMENT, "role", analytics);
    // equals is not defined on MessageBuilder, so we need to use ArgumentCaptor to inspect each field
    // manually.
    final ArgumentCaptor<IdentifyMessage.Builder> mockBuilder = ArgumentCaptor.forClass(IdentifyMessage.Builder.class);
    when(roleSupplier.get()).thenReturn("role");

    segmentTrackingClient.identify(WORKSPACE_ID);

    verify(analytics).enqueue(mockBuilder.capture());
    final IdentifyMessage actual = mockBuilder.getValue().build();
    final Map<String, Object> expectedTraits = ImmutableMap.<String, Object>builder()
        .put("airbyte_role", "role")
        .put(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION.serialize())
        .put("anonymized", IDENTITY.isAnonymousDataCollection())
        .put("deployment_env", DEPLOYMENT.getDeploymentEnv())
        .put("deployment_mode", DEPLOYMENT.getDeploymentMode())
        .put("deployment_id", DEPLOYMENT.getDeploymentId())
        .put("email", IDENTITY.getEmail().get())
        .put("subscribed_newsletter", IDENTITY.isNews())
        .put("subscribed_security", IDENTITY.isSecurityUpdates())
        .build();
    assertEquals(IDENTITY.getCustomerId().toString(), actual.userId());
    assertEquals(expectedTraits, actual.traits());
  }

  @Test
  void testTrack() {
    final ArgumentCaptor<TrackMessage.Builder> mockBuilder = ArgumentCaptor.forClass(TrackMessage.Builder.class);
    final ImmutableMap<String, Object> metadata =
        ImmutableMap.of(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION.serialize(), "user_id", IDENTITY.getCustomerId());

    segmentTrackingClient.track(WORKSPACE_ID, JUMP);

    verify(analytics).enqueue(mockBuilder.capture());
    final TrackMessage actual = mockBuilder.getValue().build();
    assertEquals(JUMP, actual.event());
    assertEquals(IDENTITY.getCustomerId().toString(), actual.userId());
    assertEquals(metadata, filterTrackedAtProperty(Objects.requireNonNull(actual.properties())));
  }

  @Test
  void testTrackWithMetadata() {
    final ArgumentCaptor<TrackMessage.Builder> mockBuilder = ArgumentCaptor.forClass(TrackMessage.Builder.class);
    final ImmutableMap<String, Object> metadata = ImmutableMap.of(
        AIRBYTE_VERSION_KEY, AIRBYTE_VERSION.serialize(),
        "email", EMAIL,
        "height", "80 meters",
        "user_id", IDENTITY.getCustomerId());

    segmentTrackingClient.track(WORKSPACE_ID, JUMP, metadata);

    verify(analytics).enqueue(mockBuilder.capture());
    final TrackMessage actual = mockBuilder.getValue().build();
    assertEquals(JUMP, actual.event());
    assertEquals(IDENTITY.getCustomerId().toString(), actual.userId());
    assertEquals(metadata, filterTrackedAtProperty(Objects.requireNonNull(actual.properties())));
  }

  private static ImmutableMap<String, Object> filterTrackedAtProperty(final Map<String, ?> properties) {
    assertTrue(properties.containsKey("tracked_at"));
    final Builder<String, Object> builder = ImmutableMap.builder();
    properties.forEach((key, value) -> {
      if (!"tracked_at".equals(key)) {
        builder.put(key, value);
      }
    });
    return builder.build();
  }

}
