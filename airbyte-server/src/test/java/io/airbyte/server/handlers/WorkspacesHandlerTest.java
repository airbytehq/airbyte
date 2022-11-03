/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionReadList;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationReadList;
import io.airbyte.api.model.generated.SlugRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceReadList;
import io.airbyte.api.model.generated.WorkspaceCreate;
import io.airbyte.api.model.generated.WorkspaceGiveFeedback;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.api.model.generated.WorkspaceRead;
import io.airbyte.api.model.generated.WorkspaceReadList;
import io.airbyte.api.model.generated.WorkspaceUpdate;
import io.airbyte.api.model.generated.WorkspaceUpdateName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.converters.NotificationConverter;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class WorkspacesHandlerTest {

  public static final String FAILURE_NOTIFICATION_WEBHOOK = "http://airbyte.notifications/failure";
  private ConfigRepository configRepository;
  private ConnectionsHandler connectionsHandler;
  private DestinationHandler destinationHandler;
  private SourceHandler sourceHandler;
  private Supplier<UUID> uuidSupplier;
  private StandardWorkspace workspace;
  private WorkspacesHandler workspacesHandler;

  private static final String TEST_EMAIL = "test@airbyte.io";
  private static final String TEST_WORKSPACE_NAME = "test workspace";
  private static final String TEST_WORKSPACE_SLUG = "test-workspace";

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    connectionsHandler = mock(ConnectionsHandler.class);
    destinationHandler = mock(DestinationHandler.class);
    sourceHandler = mock(SourceHandler.class);
    uuidSupplier = mock(Supplier.class);
    workspace = generateWorkspace();
    workspacesHandler = new WorkspacesHandler(configRepository, connectionsHandler, destinationHandler, sourceHandler, uuidSupplier);
  }

  private StandardWorkspace generateWorkspace() {
    return new StandardWorkspace()
        .withWorkspaceId(UUID.randomUUID())
        .withCustomerId(UUID.randomUUID())
        .withEmail(TEST_EMAIL)
        .withName(TEST_WORKSPACE_NAME)
        .withSlug(TEST_WORKSPACE_SLUG)
        .withInitialSetupComplete(false)
        .withDisplaySetupWizard(true)
        .withNews(false)
        .withAnonymousDataCollection(false)
        .withSecurityUpdates(false)
        .withTombstone(false)
        .withNotifications(List.of(generateNotification()));
  }

  private Notification generateNotification() {
    return new Notification()
        .withNotificationType(NotificationType.SLACK)
        .withSlackConfiguration(new SlackNotificationConfiguration()
            .withWebhook(FAILURE_NOTIFICATION_WEBHOOK));
  }

  private io.airbyte.api.model.generated.Notification generateApiNotification() {
    return new io.airbyte.api.model.generated.Notification()
        .notificationType(io.airbyte.api.model.generated.NotificationType.SLACK)
        .slackConfiguration(new io.airbyte.api.model.generated.SlackNotificationConfiguration()
            .webhook(FAILURE_NOTIFICATION_WEBHOOK));
  }

  @Test
  void testCreateWorkspace() throws JsonValidationException, IOException {
    when(configRepository.listStandardWorkspaces(false)).thenReturn(Collections.singletonList(workspace));

    final UUID uuid = UUID.randomUUID();
    when(uuidSupplier.get()).thenReturn(uuid);

    configRepository.writeStandardWorkspace(workspace);

    final WorkspaceCreate workspaceCreate = new WorkspaceCreate()
        .name("new workspace")
        .email(TEST_EMAIL)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false)
        .notifications(List.of(generateApiNotification()));

    final WorkspaceRead actualRead = workspacesHandler.createWorkspace(workspaceCreate);
    final WorkspaceRead expectedRead = new WorkspaceRead()
        .workspaceId(uuid)
        .customerId(uuid)
        .email(TEST_EMAIL)
        .name("new workspace")
        .slug("new-workspace")
        .initialSetupComplete(false)
        .displaySetupWizard(false)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false)
        .notifications(List.of(generateApiNotification()));

    assertEquals(expectedRead, actualRead);
  }

  @Test
  void testCreateWorkspaceDuplicateSlug() throws JsonValidationException, IOException {
    when(configRepository.getWorkspaceBySlugOptional(any(String.class), eq(true)))
        .thenReturn(Optional.of(workspace))
        .thenReturn(Optional.of(workspace))
        .thenReturn(Optional.empty());

    final UUID uuid = UUID.randomUUID();
    when(uuidSupplier.get()).thenReturn(uuid);

    configRepository.writeStandardWorkspace(workspace);

    final WorkspaceCreate workspaceCreate = new WorkspaceCreate()
        .name(workspace.getName())
        .email(TEST_EMAIL)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false)
        .notifications(Collections.emptyList());

    final WorkspaceRead actualRead = workspacesHandler.createWorkspace(workspaceCreate);
    final WorkspaceRead expectedRead = new WorkspaceRead()
        .workspaceId(uuid)
        .customerId(uuid)
        .email(TEST_EMAIL)
        .name(workspace.getName())
        .slug(workspace.getSlug())
        .initialSetupComplete(false)
        .displaySetupWizard(false)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false)
        .notifications(Collections.emptyList());

    assertTrue(actualRead.getSlug().startsWith(workspace.getSlug()));
    assertNotEquals(workspace.getSlug(), actualRead.getSlug());
    assertEquals(Jsons.clone(expectedRead).slug(null), Jsons.clone(actualRead).slug(null));
    final ArgumentCaptor<String> slugCaptor = ArgumentCaptor.forClass(String.class);
    verify(configRepository, times(3)).getWorkspaceBySlugOptional(slugCaptor.capture(), eq(true));
    assertEquals(3, slugCaptor.getAllValues().size());
    assertEquals(workspace.getSlug(), slugCaptor.getAllValues().get(0));
    assertTrue(slugCaptor.getAllValues().get(1).startsWith(workspace.getSlug()));
    assertTrue(slugCaptor.getAllValues().get(2).startsWith(workspace.getSlug()));

  }

  @Test
  void testDeleteWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(workspace.getWorkspaceId());

    final ConnectionRead connection = new ConnectionRead();
    final DestinationRead destination = new DestinationRead();
    final SourceRead source = new SourceRead();

    when(configRepository.getStandardWorkspace(workspace.getWorkspaceId(), false)).thenReturn(workspace);

    when(configRepository.listStandardWorkspaces(false)).thenReturn(Collections.singletonList(workspace));

    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody))
        .thenReturn(new ConnectionReadList().connections(Collections.singletonList(connection)));

    when(destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody))
        .thenReturn(new DestinationReadList().destinations(Collections.singletonList(destination)));

    when(sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody))
        .thenReturn(new SourceReadList().sources(Collections.singletonList(source)));

    workspacesHandler.deleteWorkspace(workspaceIdRequestBody);

    verify(connectionsHandler).deleteConnection(connection.getConnectionId());
    verify(destinationHandler).deleteDestination(destination);
    verify(sourceHandler).deleteSource(source);
  }

  @Test
  void testListWorkspaces() throws JsonValidationException, IOException {
    final StandardWorkspace workspace2 = generateWorkspace();

    when(configRepository.listStandardWorkspaces(false)).thenReturn(Lists.newArrayList(workspace, workspace2));

    final WorkspaceRead expectedWorkspaceRead1 = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .email(workspace.getEmail())
        .name(workspace.getName())
        .slug(workspace.getSlug())
        .initialSetupComplete(workspace.getInitialSetupComplete())
        .displaySetupWizard(workspace.getDisplaySetupWizard())
        .news(workspace.getNews())
        .anonymousDataCollection(workspace.getAnonymousDataCollection())
        .securityUpdates(workspace.getSecurityUpdates())
        .notifications(List.of(generateApiNotification()));

    final WorkspaceRead expectedWorkspaceRead2 = new WorkspaceRead()
        .workspaceId(workspace2.getWorkspaceId())
        .customerId(workspace2.getCustomerId())
        .email(workspace2.getEmail())
        .name(workspace2.getName())
        .slug(workspace2.getSlug())
        .initialSetupComplete(workspace2.getInitialSetupComplete())
        .displaySetupWizard(workspace2.getDisplaySetupWizard())
        .news(workspace2.getNews())
        .anonymousDataCollection(workspace2.getAnonymousDataCollection())
        .securityUpdates(workspace2.getSecurityUpdates())
        .notifications(List.of(generateApiNotification()));

    final WorkspaceReadList actualWorkspaceReadList = workspacesHandler.listWorkspaces();

    assertEquals(Lists.newArrayList(expectedWorkspaceRead1, expectedWorkspaceRead2),
        actualWorkspaceReadList.getWorkspaces());
  }

  @Test
  void testGetWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getStandardWorkspace(workspace.getWorkspaceId(), false)).thenReturn(workspace);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(workspace.getWorkspaceId());

    final WorkspaceRead workspaceRead = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .email(TEST_EMAIL)
        .name(TEST_WORKSPACE_NAME)
        .slug(TEST_WORKSPACE_SLUG)
        .initialSetupComplete(false)
        .displaySetupWizard(true)
        .news(false)
        .anonymousDataCollection(false)
        .securityUpdates(false)
        .notifications(List.of(generateApiNotification()));

    assertEquals(workspaceRead, workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Test
  void testGetWorkspaceBySlug() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getWorkspaceBySlug("default", false)).thenReturn(workspace);

    final SlugRequestBody slugRequestBody = new SlugRequestBody().slug("default");
    final WorkspaceRead workspaceRead = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .email(TEST_EMAIL)
        .name(workspace.getName())
        .slug(workspace.getSlug())
        .initialSetupComplete(workspace.getInitialSetupComplete())
        .displaySetupWizard(workspace.getDisplaySetupWizard())
        .news(workspace.getNews())
        .anonymousDataCollection(workspace.getAnonymousDataCollection())
        .securityUpdates(workspace.getSecurityUpdates())
        .notifications(NotificationConverter.toApiList(workspace.getNotifications()));

    assertEquals(workspaceRead, workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Test
  void testUpdateWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    final io.airbyte.api.model.generated.Notification apiNotification = generateApiNotification();
    apiNotification.getSlackConfiguration().webhook("updated");
    final WorkspaceUpdate workspaceUpdate = new WorkspaceUpdate()
        .workspaceId(workspace.getWorkspaceId())
        .anonymousDataCollection(true)
        .securityUpdates(false)
        .news(false)
        .initialSetupComplete(true)
        .displaySetupWizard(false)
        .notifications(List.of(apiNotification));

    final Notification expectedNotification = generateNotification();
    expectedNotification.getSlackConfiguration().withWebhook("updated");
    final StandardWorkspace expectedWorkspace = new StandardWorkspace()
        .withWorkspaceId(workspace.getWorkspaceId())
        .withCustomerId(workspace.getCustomerId())
        .withEmail(TEST_EMAIL)
        .withName(TEST_WORKSPACE_NAME)
        .withSlug(TEST_WORKSPACE_SLUG)
        .withAnonymousDataCollection(true)
        .withSecurityUpdates(false)
        .withNews(false)
        .withInitialSetupComplete(true)
        .withDisplaySetupWizard(false)
        .withTombstone(false)
        .withNotifications(List.of(expectedNotification));

    when(configRepository.getStandardWorkspace(workspace.getWorkspaceId(), false))
        .thenReturn(workspace)
        .thenReturn(expectedWorkspace);

    final WorkspaceRead actualWorkspaceRead = workspacesHandler.updateWorkspace(workspaceUpdate);

    final io.airbyte.api.model.generated.Notification expectedNotificationRead = generateApiNotification();
    expectedNotificationRead.getSlackConfiguration().webhook("updated");
    final WorkspaceRead expectedWorkspaceRead = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .email(TEST_EMAIL)
        .name(TEST_WORKSPACE_NAME)
        .slug(TEST_WORKSPACE_SLUG)
        .initialSetupComplete(true)
        .displaySetupWizard(false)
        .news(false)
        .anonymousDataCollection(true)
        .securityUpdates(false)
        .notifications(List.of(expectedNotificationRead));

    verify(configRepository).writeStandardWorkspace(expectedWorkspace);

    assertEquals(expectedWorkspaceRead, actualWorkspaceRead);
  }

  @Test
  @DisplayName("Updating workspace name should update name and slug")
  void testUpdateWorkspaceNoNameUpdate() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WorkspaceUpdateName workspaceUpdate = new WorkspaceUpdateName()
        .workspaceId(workspace.getWorkspaceId())
        .name("New Workspace Name");

    final StandardWorkspace expectedWorkspace = new StandardWorkspace()
        .withWorkspaceId(workspace.getWorkspaceId())
        .withCustomerId(workspace.getCustomerId())
        .withEmail(TEST_EMAIL)
        .withName("New Workspace Name")
        .withSlug("new-workspace-name")
        .withAnonymousDataCollection(workspace.getAnonymousDataCollection())
        .withSecurityUpdates(workspace.getSecurityUpdates())
        .withNews(workspace.getNews())
        .withInitialSetupComplete(workspace.getInitialSetupComplete())
        .withDisplaySetupWizard(workspace.getDisplaySetupWizard())
        .withTombstone(false)
        .withNotifications(workspace.getNotifications());

    when(configRepository.getStandardWorkspace(workspace.getWorkspaceId(), false))
        .thenReturn(workspace)
        .thenReturn(expectedWorkspace);

    final WorkspaceRead actualWorkspaceRead = workspacesHandler.updateWorkspaceName(workspaceUpdate);

    final WorkspaceRead expectedWorkspaceRead = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .email(TEST_EMAIL)
        .name("New Workspace Name")
        .slug("new-workspace-name")
        .initialSetupComplete(workspace.getInitialSetupComplete())
        .displaySetupWizard(workspace.getDisplaySetupWizard())
        .news(workspace.getNews())
        .anonymousDataCollection(workspace.getAnonymousDataCollection())
        .securityUpdates(workspace.getSecurityUpdates())
        .notifications(List.of(generateApiNotification()));

    verify(configRepository).writeStandardWorkspace(expectedWorkspace);

    assertEquals(expectedWorkspaceRead, actualWorkspaceRead);
  }

  @Test
  void testSetFeedbackDone() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WorkspaceGiveFeedback workspaceGiveFeedback = new WorkspaceGiveFeedback()
        .workspaceId(UUID.randomUUID());

    workspacesHandler.setFeedbackDone(workspaceGiveFeedback);

    verify(configRepository).setFeedback(workspaceGiveFeedback.getWorkspaceId());
  }

}
