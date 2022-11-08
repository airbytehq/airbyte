/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.github.slugify.Slugify;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.base.Strings;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.Geography;
import io.airbyte.api.model.generated.Notification;
import io.airbyte.api.model.generated.NotificationRead;
import io.airbyte.api.model.generated.NotificationRead.StatusEnum;
import io.airbyte.api.model.generated.SlugRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.WorkspaceCreate;
import io.airbyte.api.model.generated.WorkspaceGiveFeedback;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.api.model.generated.WorkspaceRead;
import io.airbyte.api.model.generated.WorkspaceReadList;
import io.airbyte.api.model.generated.WorkspaceUpdate;
import io.airbyte.api.model.generated.WorkspaceUpdateName;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.notification.NotificationClient;
import io.airbyte.server.converters.ApiPojoConverters;
import io.airbyte.server.converters.NotificationConverter;
import io.airbyte.server.converters.WorkspaceWebhookConfigsConverter;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.server.errors.InternalServerKnownException;
import io.airbyte.server.errors.ValueConflictKnownException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WorkspacesHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkspacesHandler.class);
  private final ConfigRepository configRepository;
  private final SecretsRepositoryWriter secretsRepositoryWriter;
  private final ConnectionsHandler connectionsHandler;
  private final DestinationHandler destinationHandler;
  private final SourceHandler sourceHandler;
  private final Supplier<UUID> uuidSupplier;
  private final Slugify slugify;

  public WorkspacesHandler(final ConfigRepository configRepository,
                           final SecretsRepositoryWriter secretsRepositoryWriter,
                           final ConnectionsHandler connectionsHandler,
                           final DestinationHandler destinationHandler,
                           final SourceHandler sourceHandler) {
    this(configRepository, secretsRepositoryWriter, connectionsHandler, destinationHandler, sourceHandler, UUID::randomUUID);
  }

  @VisibleForTesting
  WorkspacesHandler(final ConfigRepository configRepository,
                    final SecretsRepositoryWriter secretsRepositoryWriter,
                    final ConnectionsHandler connectionsHandler,
                    final DestinationHandler destinationHandler,
                    final SourceHandler sourceHandler,
                    final Supplier<UUID> uuidSupplier) {
    this.configRepository = configRepository;
    this.secretsRepositoryWriter = secretsRepositoryWriter;
    this.connectionsHandler = connectionsHandler;
    this.destinationHandler = destinationHandler;
    this.sourceHandler = sourceHandler;
    this.uuidSupplier = uuidSupplier;
    this.slugify = new Slugify();
  }

  public WorkspaceRead createWorkspace(final WorkspaceCreate workspaceCreate)
      throws JsonValidationException, IOException, ValueConflictKnownException {

    final String email = workspaceCreate.getEmail();
    final Boolean anonymousDataCollection = workspaceCreate.getAnonymousDataCollection();
    final Boolean news = workspaceCreate.getNews();
    final Boolean securityUpdates = workspaceCreate.getSecurityUpdates();
    final Boolean displaySetupWizard = workspaceCreate.getDisplaySetupWizard();

    // if not set on the workspaceCreate, set the defaultGeography to AUTO
    final io.airbyte.config.Geography defaultGeography = workspaceCreate.getDefaultGeography() != null
        ? Enums.convertTo(workspaceCreate.getDefaultGeography(), io.airbyte.config.Geography.class)
        : io.airbyte.config.Geography.AUTO;

    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(uuidSupplier.get())
        .withCustomerId(uuidSupplier.get())
        .withName(workspaceCreate.getName())
        .withSlug(generateUniqueSlug(workspaceCreate.getName()))
        .withInitialSetupComplete(false)
        .withAnonymousDataCollection(anonymousDataCollection != null ? anonymousDataCollection : false)
        .withNews(news != null ? news : false)
        .withSecurityUpdates(securityUpdates != null ? securityUpdates : false)
        .withDisplaySetupWizard(displaySetupWizard != null ? displaySetupWizard : false)
        .withTombstone(false)
        .withNotifications(NotificationConverter.toConfigList(workspaceCreate.getNotifications()))
        .withDefaultGeography(defaultGeography)
        .withWebhookOperationConfigs(WorkspaceWebhookConfigsConverter.toPersistenceWrite(workspaceCreate.getWebhookConfigs(), uuidSupplier));

    if (!Strings.isNullOrEmpty(email)) {
      workspace.withEmail(email);
    }

    return persistStandardWorkspace(workspace);
  }

  public void deleteWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // get existing implementation
    final StandardWorkspace persistedWorkspace = configRepository.getStandardWorkspaceNoSecrets(workspaceIdRequestBody.getWorkspaceId(), false);

    // disable all connections associated with this workspace
    for (final ConnectionRead connectionRead : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      connectionsHandler.deleteConnection(connectionRead.getConnectionId());
    }

    // disable all destinations associated with this workspace
    for (final DestinationRead destinationRead : destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody).getDestinations()) {
      destinationHandler.deleteDestination(destinationRead);
    }

    // disable all sources associated with this workspace
    for (final SourceRead sourceRead : sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody).getSources()) {
      sourceHandler.deleteSource(sourceRead);
    }

    persistedWorkspace.withTombstone(true);
    persistStandardWorkspace(persistedWorkspace);
  }

  public WorkspaceReadList listWorkspaces() throws JsonValidationException, IOException {
    final List<WorkspaceRead> reads = configRepository.listStandardWorkspaces(false).stream()
        .map(WorkspacesHandler::buildWorkspaceRead)
        .collect(Collectors.toList());
    return new WorkspaceReadList().workspaces(reads);
  }

  public WorkspaceRead getWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID workspaceId = workspaceIdRequestBody.getWorkspaceId();
    final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, false);
    return buildWorkspaceRead(workspace);
  }

  @SuppressWarnings("unused")
  public WorkspaceRead getWorkspaceBySlug(final SlugRequestBody slugRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // for now we assume there is one workspace and it has a default uuid.
    final StandardWorkspace workspace = configRepository.getWorkspaceBySlug(slugRequestBody.getSlug(), false);
    return buildWorkspaceRead(workspace);
  }

  public WorkspaceRead getWorkspaceByConnectionId(final ConnectionIdRequestBody connectionIdRequestBody) {
    final StandardWorkspace workspace = configRepository.getStandardWorkspaceFromConnection(connectionIdRequestBody.getConnectionId(), false);
    return buildWorkspaceRead(workspace);
  }

  public WorkspaceRead updateWorkspace(final WorkspaceUpdate workspacePatch) throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID workspaceId = workspacePatch.getWorkspaceId();

    LOGGER.debug("Starting updateWorkspace for workspaceId {}...", workspaceId);
    LOGGER.debug("Incoming workspacePatch: {}", workspacePatch);

    final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, false);
    LOGGER.debug("Initial workspace: {}", workspace);

    validateWorkspacePatch(workspace, workspacePatch);

    LOGGER.debug("Initial WorkspaceRead: {}", buildWorkspaceRead(workspace));

    applyPatchToStandardWorkspace(workspace, workspacePatch);

    LOGGER.debug("Patched Workspace before persisting: {}", workspace);

    persistStandardWorkspace(workspace);

    // after updating email or tracking info, we need to re-identify the instance.
    TrackingClientSingleton.get().identify(workspaceId);

    return buildWorkspaceReadFromId(workspaceId);
  }

  public WorkspaceRead updateWorkspaceName(final WorkspaceUpdateName workspaceUpdateName)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID workspaceId = workspaceUpdateName.getWorkspaceId();

    final StandardWorkspace persistedWorkspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, false);

    persistedWorkspace
        .withName(workspaceUpdateName.getName())
        .withSlug(generateUniqueSlug(workspaceUpdateName.getName()));

    persistStandardWorkspace(persistedWorkspace);

    return buildWorkspaceReadFromId(workspaceId);
  }

  public NotificationRead tryNotification(final Notification notification) {
    try {
      final NotificationClient notificationClient = NotificationClient.createNotificationClient(NotificationConverter.toConfig(notification));
      final String messageFormat = "Hello World! This is a test from Airbyte to try %s notification settings for sync %s";
      final boolean failureNotified = notificationClient.notifyFailure(String.format(messageFormat, notification.getNotificationType(), "failures"));
      final boolean successNotified = notificationClient.notifySuccess(String.format(messageFormat, notification.getNotificationType(), "successes"));
      if (failureNotified || successNotified) {
        return new NotificationRead().status(StatusEnum.SUCCEEDED);
      }
    } catch (final IllegalArgumentException e) {
      throw new IdNotFoundKnownException(e.getMessage(), notification.getNotificationType().name(), e);
    } catch (final IOException | InterruptedException e) {
      return new NotificationRead().status(StatusEnum.FAILED).message(e.getMessage());
    }
    return new NotificationRead().status(StatusEnum.FAILED);
  }

  public void setFeedbackDone(final WorkspaceGiveFeedback workspaceGiveFeedback)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    configRepository.setFeedback(workspaceGiveFeedback.getWorkspaceId());
  }

  private WorkspaceRead buildWorkspaceReadFromId(final UUID workspaceId) throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, false);
    return buildWorkspaceRead(workspace);
  }

  private String generateUniqueSlug(final String workspaceName) throws JsonValidationException, IOException {
    final String proposedSlug = slugify.slugify(workspaceName);

    // todo (cgardens) - this is going to be too expensive once there are too many workspaces. needs to
    // be replaced with an actual sql query. e.g. SELECT COUNT(*) WHERE slug=%s;
    boolean isSlugUsed = configRepository.getWorkspaceBySlugOptional(proposedSlug, true).isPresent();
    String resolvedSlug = proposedSlug;
    final int MAX_ATTEMPTS = 10;
    int count = 0;
    while (isSlugUsed) {
      // todo (cgardens) - this is still susceptible to a race condition where we randomly generate the
      // same slug in two different threads. this should be very unlikely. we can fix this by exposing
      // database transaction, but that is not something we can do quickly.
      resolvedSlug = proposedSlug + "-" + RandomStringUtils.randomAlphabetic(8);
      isSlugUsed = configRepository.getWorkspaceBySlugOptional(resolvedSlug, true).isPresent();
      count++;
      if (count > MAX_ATTEMPTS) {
        throw new InternalServerKnownException(String.format("could not generate a valid slug after %s tries.", MAX_ATTEMPTS));
      }
    }

    return resolvedSlug;
  }

  private static WorkspaceRead buildWorkspaceRead(final StandardWorkspace workspace) {
    final WorkspaceRead result = new WorkspaceRead()
        .workspaceId(workspace.getWorkspaceId())
        .customerId(workspace.getCustomerId())
        .email(workspace.getEmail())
        .name(workspace.getName())
        .slug(workspace.getSlug())
        .initialSetupComplete(workspace.getInitialSetupComplete())
        .displaySetupWizard(workspace.getDisplaySetupWizard())
        .anonymousDataCollection(workspace.getAnonymousDataCollection())
        .news(workspace.getNews())
        .securityUpdates(workspace.getSecurityUpdates())
        .notifications(NotificationConverter.toApiList(workspace.getNotifications()))
        .defaultGeography(Enums.convertTo(workspace.getDefaultGeography(), Geography.class));
    // Add read-only webhook configs.
    if (workspace.getWebhookOperationConfigs() != null) {
      result.setWebhookConfigs(WorkspaceWebhookConfigsConverter.toApiReads(workspace.getWebhookOperationConfigs()));
    }
    return result;
  }

  private void validateWorkspacePatch(final StandardWorkspace persistedWorkspace, final WorkspaceUpdate workspacePatch) {
    Preconditions.checkArgument(persistedWorkspace.getWorkspaceId().equals(workspacePatch.getWorkspaceId()));
  }

  private void applyPatchToStandardWorkspace(final StandardWorkspace workspace, final WorkspaceUpdate workspacePatch) {
    if (workspacePatch.getAnonymousDataCollection() != null) {
      workspace.setAnonymousDataCollection(workspacePatch.getAnonymousDataCollection());
    }
    if (workspacePatch.getNews() != null) {
      workspace.setNews(workspacePatch.getNews());
    }
    if (workspacePatch.getDisplaySetupWizard() != null) {
      workspace.setDisplaySetupWizard(workspacePatch.getDisplaySetupWizard());
    }
    if (workspacePatch.getSecurityUpdates() != null) {
      workspace.setSecurityUpdates(workspacePatch.getSecurityUpdates());
    }
    if (!Strings.isNullOrEmpty(workspacePatch.getEmail())) {
      workspace.setEmail(workspacePatch.getEmail());
    }
    if (workspacePatch.getInitialSetupComplete() != null) {
      workspace.setInitialSetupComplete(workspacePatch.getInitialSetupComplete());
    }
    if (workspacePatch.getNotifications() != null) {
      workspace.setNotifications(NotificationConverter.toConfigList(workspacePatch.getNotifications()));
    }
    if (workspacePatch.getDefaultGeography() != null) {
      workspace.setDefaultGeography(ApiPojoConverters.toPersistenceGeography(workspacePatch.getDefaultGeography()));
    }
    if (workspacePatch.getWebhookConfigs() != null) {
      workspace.setWebhookOperationConfigs(WorkspaceWebhookConfigsConverter.toPersistenceWrite(workspacePatch.getWebhookConfigs(), uuidSupplier));
    }
  }

  private WorkspaceRead persistStandardWorkspace(final StandardWorkspace workspace) throws JsonValidationException, IOException {
    secretsRepositoryWriter.writeWorkspace(workspace);
    return buildWorkspaceRead(workspace);
  }

}
