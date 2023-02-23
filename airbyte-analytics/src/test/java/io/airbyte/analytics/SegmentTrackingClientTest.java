/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import static io.airbyte.analytics.SegmentTrackingClient.AIRBYTE_ANALYTIC_SOURCE_HEADER;
import static io.airbyte.analytics.SegmentTrackingClient.AIRBYTE_SOURCE;
import static io.airbyte.analytics.SegmentTrackingClient.AIRBYTE_VERSION_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
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
import io.micronaut.http.HttpHeaders;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.context.ServerRequestContext;
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
  private static final String JUMP = "jump";
  private static final String EMAIL_KEY = "email";

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
        .put(EMAIL_KEY, IDENTITY.getEmail().get())
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
        .put(EMAIL_KEY, IDENTITY.getEmail().get())
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
        EMAIL_KEY, EMAIL,
        "height", "80 meters",
        "user_id", IDENTITY.getCustomerId());

    segmentTrackingClient.track(WORKSPACE_ID, JUMP, metadata);

    verify(analytics).enqueue(mockBuilder.capture());
    final TrackMessage actual = mockBuilder.getValue().build();
    assertEquals(JUMP, actual.event());
    assertEquals(IDENTITY.getCustomerId().toString(), actual.userId());
    assertEquals(metadata, filterTrackedAtProperty(Objects.requireNonNull(actual.properties())));
  }

  @Test
  void testTrackNullWorkspace() {
    segmentTrackingClient.track(null, JUMP);

    verify(analytics, never()).enqueue(any());
  }

  @Test
  void testTrackAirbyteAnalyticSource() {
    final String analyticSource = "test";
    final HttpHeaders httpHeaders = mock(HttpHeaders.class);
    final HttpRequest<?> httpRequest = mock(HttpRequest.class);

    when(httpHeaders.get(AIRBYTE_ANALYTIC_SOURCE_HEADER)).thenReturn(analyticSource);
    when(httpRequest.getHeaders()).thenReturn(httpHeaders);
    ServerRequestContext.set(httpRequest);

    final ArgumentCaptor<TrackMessage.Builder> mockBuilder = ArgumentCaptor.forClass(TrackMessage.Builder.class);
    final ImmutableMap<String, Object> metadata = ImmutableMap.of(
        AIRBYTE_VERSION_KEY, AIRBYTE_VERSION.serialize(),
        EMAIL_KEY, EMAIL,
        "height", "80 meters",
        "user_id", IDENTITY.getCustomerId());

    segmentTrackingClient.track(WORKSPACE_ID, JUMP, metadata);

    verify(analytics).enqueue(mockBuilder.capture());
    final TrackMessage actual = mockBuilder.getValue().build();
    assertEquals(analyticSource, actual.properties().get(AIRBYTE_SOURCE));
  }

  private static ImmutableMap<String, Object> filterTrackedAtProperty(final Map<String, ?> properties) {
    final String trackedAtKey = "tracked_at";
    assertTrue(properties.containsKey(trackedAtKey));
    final Builder<String, Object> builder = ImmutableMap.builder();
    properties.forEach((key, value) -> {
      if (!trackedAtKey.equals(key)) {
        builder.put(key, value);
      }
    });
    return builder.build();
  }

}
