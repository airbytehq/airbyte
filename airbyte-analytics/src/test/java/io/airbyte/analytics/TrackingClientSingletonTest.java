/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.analytics;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Function;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class TrackingClientSingletonTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final String AIRBYTE_VERSION = "dev";
  private static final String EMAIL = "a@airbyte.io";
  private static final Deployment DEPLOYMENT = new Deployment(Configs.DeploymentMode.OSS, UUID.randomUUID(), WorkerEnvironment.DOCKER);
  private static final TrackingIdentity IDENTITY = new TrackingIdentity(AIRBYTE_VERSION, UUID.randomUUID(), EMAIL, false, false, true);
  private static final Function<UUID, TrackingIdentity> MOCK_TRACKING_IDENTITY = (workspaceId) -> IDENTITY;

  private ConfigRepository configRepository;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    // equivalent of resetting TrackingClientSingleton to uninitialized state.
    TrackingClientSingleton.initialize(null);
  }

  @Test
  void testCreateTrackingClientLogging() {
    assertTrue(
        TrackingClientSingleton.createTrackingClient(
            Configs.TrackingStrategy.LOGGING,
            DEPLOYMENT,
            "role",
            MOCK_TRACKING_IDENTITY) instanceof LoggingTrackingClient);
  }

  @Test
  void testCreateTrackingClientSegment() {
    assertTrue(
        TrackingClientSingleton.createTrackingClient(
            Configs.TrackingStrategy.SEGMENT,
            DEPLOYMENT,
            "role",
            MOCK_TRACKING_IDENTITY) instanceof SegmentTrackingClient);
  }

  @Test
  void testGet() {
    TrackingClient client = mock(TrackingClient.class);
    TrackingClientSingleton.initialize(client);
    assertEquals(client, TrackingClientSingleton.get());
  }

  @Test
  void testGetUninitialized() {
    assertTrue(TrackingClientSingleton.get() instanceof LoggingTrackingClient);
  }

  @Test
  void testGetTrackingIdentityRespectsWorkspaceId() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace1 = new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withCustomerId(UUID.randomUUID());
    final StandardWorkspace workspace2 = new StandardWorkspace().withWorkspaceId(UUID.randomUUID()).withCustomerId(UUID.randomUUID());

    when(configRepository.getStandardWorkspace(workspace1.getWorkspaceId(), true)).thenReturn(workspace1);
    when(configRepository.getStandardWorkspace(workspace2.getWorkspaceId(), true)).thenReturn(workspace2);

    final TrackingIdentity workspace1Actual =
        TrackingClientSingleton.getTrackingIdentity(configRepository, AIRBYTE_VERSION, workspace1.getWorkspaceId());
    final TrackingIdentity workspace2Actual =
        TrackingClientSingleton.getTrackingIdentity(configRepository, AIRBYTE_VERSION, workspace2.getWorkspaceId());
    final TrackingIdentity workspace1Expected = new TrackingIdentity(AIRBYTE_VERSION, workspace1.getCustomerId(), null, null, null, null);
    final TrackingIdentity workspace2Expected = new TrackingIdentity(AIRBYTE_VERSION, workspace2.getCustomerId(), null, null, null, null);

    assertEquals(workspace1Expected, workspace1Actual);
    assertEquals(workspace2Expected, workspace2Actual);
  }

  @Test
  void testGetTrackingIdentityInitialSetupNotComplete() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withCustomerId(UUID.randomUUID());

    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true)).thenReturn(workspace);

    final TrackingIdentity actual = TrackingClientSingleton.getTrackingIdentity(configRepository, AIRBYTE_VERSION, WORKSPACE_ID);
    final TrackingIdentity expected = new TrackingIdentity(AIRBYTE_VERSION, workspace.getCustomerId(), null, null, null, null);

    assertEquals(expected, actual);
  }

  @Test
  void testGetTrackingIdentityNonAnonymous() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID)
        .withCustomerId(UUID.randomUUID())
        .withEmail(EMAIL)
        .withAnonymousDataCollection(false)
        .withNews(true)
        .withSecurityUpdates(true);

    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true)).thenReturn(workspace);

    final TrackingIdentity actual = TrackingClientSingleton.getTrackingIdentity(configRepository, AIRBYTE_VERSION, WORKSPACE_ID);
    final TrackingIdentity expected = new TrackingIdentity(AIRBYTE_VERSION, workspace.getCustomerId(), workspace.getEmail(), false, true, true);

    assertEquals(expected, actual);
  }

  @Test
  void testGetTrackingIdentityAnonymous() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID)
        .withCustomerId(UUID.randomUUID())
        .withEmail("a@airbyte.io")
        .withAnonymousDataCollection(true)
        .withNews(true)
        .withSecurityUpdates(true);

    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true)).thenReturn(workspace);

    final TrackingIdentity actual = TrackingClientSingleton.getTrackingIdentity(configRepository, AIRBYTE_VERSION, WORKSPACE_ID);
    final TrackingIdentity expected = new TrackingIdentity(AIRBYTE_VERSION, workspace.getCustomerId(), null, true, true, true);

    assertEquals(expected, actual);
  }

}
