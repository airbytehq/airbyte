/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.CustomDestinationDefinitionCreate;
import io.airbyte.api.model.generated.DestinationDefinitionCreate;
import io.airbyte.api.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionRead;
import io.airbyte.api.model.generated.DestinationDefinitionReadList;
import io.airbyte.api.model.generated.DestinationDefinitionUpdate;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationReadList;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionRead;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionReadList;
import io.airbyte.api.model.generated.ReleaseStage;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.ActorType;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.server.errors.UnsupportedProtocolVersionException;
import io.airbyte.server.scheduler.SynchronousJobMetadata;
import io.airbyte.server.scheduler.SynchronousResponse;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.time.LocalDate;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class DestinationDefinitionsHandlerTest {

  private static final String TODAY_DATE_STRING = LocalDate.now().toString();
  private static final String DEFAULT_PROTOCOL_VERSION = "0.2.0";

  private ConfigRepository configRepository;
  private StandardDestinationDefinition destinationDefinition;
  private DestinationDefinitionsHandler destinationDefinitionsHandler;
  private Supplier<UUID> uuidSupplier;
  private SynchronousSchedulerClient schedulerSynchronousClient;
  private AirbyteGithubStore githubStore;
  private DestinationHandler destinationHandler;
  private UUID workspaceId;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    uuidSupplier = mock(Supplier.class);
    destinationDefinition = generateDestinationDefinition();
    schedulerSynchronousClient = spy(SynchronousSchedulerClient.class);
    githubStore = mock(AirbyteGithubStore.class);
    destinationHandler = mock(DestinationHandler.class);
    workspaceId = UUID.randomUUID();

    destinationDefinitionsHandler = new DestinationDefinitionsHandler(
        configRepository,
        uuidSupplier,
        schedulerSynchronousClient,
        githubStore,
        destinationHandler);
  }

  private StandardDestinationDefinition generateDestinationDefinition() {
    final ConnectorSpecification spec = new ConnectorSpecification()
        .withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo", "bar")));

    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withName("presto")
        .withDockerImageTag("12.3")
        .withDockerRepository("repo")
        .withDocumentationUrl("https://hulu.com")
        .withIcon("http.svg")
        .withSpec(spec)
        .withProtocolVersion("0.2.2")
        .withTombstone(false)
        .withReleaseStage(StandardDestinationDefinition.ReleaseStage.ALPHA)
        .withReleaseDate(TODAY_DATE_STRING)
        .withResourceRequirements(new ActorDefinitionResourceRequirements().withDefault(new ResourceRequirements().withCpuRequest("2")));
  }

  @Test
  @DisplayName("listDestinationDefinition should return the right list")
  void testListDestinations() throws JsonValidationException, IOException, URISyntaxException {
    final StandardDestinationDefinition destination2 = generateDestinationDefinition();

    when(configRepository.listStandardDestinationDefinitions(false)).thenReturn(Lists.newArrayList(destinationDefinition, destination2));

    final DestinationDefinitionRead expectedDestinationDefinitionRead1 = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destinationDefinition.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionRead expectedDestinationDefinitionRead2 = new DestinationDefinitionRead()
        .destinationDefinitionId(destination2.getDestinationDefinitionId())
        .name(destination2.getName())
        .dockerRepository(destination2.getDockerRepository())
        .dockerImageTag(destination2.getDockerImageTag())
        .documentationUrl(new URI(destination2.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destination2.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination2.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionReadList actualDestinationDefinitionReadList = destinationDefinitionsHandler.listDestinationDefinitions();

    assertEquals(
        Lists.newArrayList(expectedDestinationDefinitionRead1, expectedDestinationDefinitionRead2),
        actualDestinationDefinitionReadList.getDestinationDefinitions());
  }

  @Test
  @DisplayName("listDestinationDefinitionsForWorkspace should return the right list")
  void testListDestinationDefinitionsForWorkspace() throws IOException, URISyntaxException {
    final StandardDestinationDefinition destination2 = generateDestinationDefinition();

    when(configRepository.listPublicDestinationDefinitions(false)).thenReturn(Lists.newArrayList(destinationDefinition));
    when(configRepository.listGrantedDestinationDefinitions(workspaceId, false)).thenReturn(Lists.newArrayList(destination2));

    final DestinationDefinitionRead expectedDestinationDefinitionRead1 = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destinationDefinition.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionRead expectedDestinationDefinitionRead2 = new DestinationDefinitionRead()
        .destinationDefinitionId(destination2.getDestinationDefinitionId())
        .name(destination2.getName())
        .dockerRepository(destination2.getDockerRepository())
        .dockerImageTag(destination2.getDockerImageTag())
        .documentationUrl(new URI(destination2.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destination2.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination2.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionReadList actualDestinationDefinitionReadList = destinationDefinitionsHandler
        .listDestinationDefinitionsForWorkspace(new WorkspaceIdRequestBody().workspaceId(workspaceId));

    assertEquals(
        Lists.newArrayList(expectedDestinationDefinitionRead1, expectedDestinationDefinitionRead2),
        actualDestinationDefinitionReadList.getDestinationDefinitions());
  }

  @Test
  @DisplayName("listPrivateDestinationDefinitions should return the right list")
  void testListPrivateDestinationDefinitions() throws IOException, URISyntaxException {
    final StandardDestinationDefinition destinationDefinition2 = generateDestinationDefinition();

    when(configRepository.listGrantableDestinationDefinitions(workspaceId, false)).thenReturn(
        Lists.newArrayList(
            Map.entry(destinationDefinition, false),
            Map.entry(destinationDefinition2, true)));

    final DestinationDefinitionRead expectedDestinationDefinitionRead1 = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destinationDefinition.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionRead expectedDestinationDefinitionRead2 = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition2.getDestinationDefinitionId())
        .name(destinationDefinition2.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destinationDefinition2.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final PrivateDestinationDefinitionRead expectedDestinationDefinitionOptInRead1 =
        new PrivateDestinationDefinitionRead().destinationDefinition(expectedDestinationDefinitionRead1).granted(false);

    final PrivateDestinationDefinitionRead expectedDestinationDefinitionOptInRead2 =
        new PrivateDestinationDefinitionRead().destinationDefinition(expectedDestinationDefinitionRead2).granted(true);

    final PrivateDestinationDefinitionReadList actualDestinationDefinitionOptInReadList =
        destinationDefinitionsHandler.listPrivateDestinationDefinitions(
            new WorkspaceIdRequestBody().workspaceId(workspaceId));

    assertEquals(
        Lists.newArrayList(expectedDestinationDefinitionOptInRead1, expectedDestinationDefinitionOptInRead2),
        actualDestinationDefinitionOptInReadList.getDestinationDefinitions());
  }

  @Test
  @DisplayName("getDestinationDefinition should return the right destination")
  void testGetDestination() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);

    final DestinationDefinitionRead expectedDestinationDefinitionRead = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destinationDefinition.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody = new DestinationDefinitionIdRequestBody()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId());

    final DestinationDefinitionRead actualDestinationDefinitionRead =
        destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody);

    assertEquals(expectedDestinationDefinitionRead, actualDestinationDefinitionRead);
  }

  @Test
  @DisplayName("getDestinationDefinitionForWorkspace should throw an exception for a missing grant")
  void testGetDefinitionWithoutGrantForWorkspace() throws IOException {
    when(configRepository.workspaceCanUseDefinition(destinationDefinition.getDestinationDefinitionId(), workspaceId))
        .thenReturn(false);

    final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId = new DestinationDefinitionIdWithWorkspaceId()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .workspaceId(workspaceId);

    assertThrows(IdNotFoundKnownException.class,
        () -> destinationDefinitionsHandler.getDestinationDefinitionForWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Test
  @DisplayName("getDestinationDefinitionForWorkspace should return the destination if the grant exists")
  void testGetDefinitionWithGrantForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.workspaceCanUseDefinition(destinationDefinition.getDestinationDefinitionId(), workspaceId))
        .thenReturn(true);
    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);

    final DestinationDefinitionRead expectedDestinationDefinitionRead = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destinationDefinition.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId = new DestinationDefinitionIdWithWorkspaceId()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .workspaceId(workspaceId);

    final DestinationDefinitionRead actualDestinationDefinitionRead = destinationDefinitionsHandler
        .getDestinationDefinitionForWorkspace(destinationDefinitionIdWithWorkspaceId);

    assertEquals(expectedDestinationDefinitionRead, actualDestinationDefinitionRead);
  }

  @Test
  @DisplayName("createDestinationDefinition should correctly create a destinationDefinition")
  void testCreateDestinationDefinition() throws URISyntaxException, IOException, JsonValidationException {
    final StandardDestinationDefinition destination = generateDestinationDefinition();
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());

    when(uuidSupplier.get()).thenReturn(destination.getDestinationDefinitionId());
    when(schedulerSynchronousClient.createGetSpecJob(imageName)).thenReturn(new SynchronousResponse<>(
        destination.getSpec(),
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final DestinationDefinitionCreate create = new DestinationDefinitionCreate()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .icon(destination.getIcon())
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionRead expectedRead = new DestinationDefinitionRead()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .destinationDefinitionId(destination.getDestinationDefinitionId())
        .icon(DestinationDefinitionsHandler.loadIcon(destination.getIcon()))
        .protocolVersion(DEFAULT_PROTOCOL_VERSION)
        .releaseStage(ReleaseStage.CUSTOM)
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionRead actualRead = destinationDefinitionsHandler.createPrivateDestinationDefinition(create);

    assertEquals(expectedRead, actualRead);
    verify(schedulerSynchronousClient).createGetSpecJob(imageName);
    verify(configRepository).writeStandardDestinationDefinition(destination
        .withProtocolVersion(DEFAULT_PROTOCOL_VERSION)
        .withReleaseDate(null)
        .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM));
  }

  @Test
  @DisplayName("createDestinationDefinition should not create a destinationDefinition with unsupported protocol version")
  void testCreateDestinationDefinitionShouldCheckProtocolVersion() throws URISyntaxException, IOException, JsonValidationException {
    final String invalidProtocolVersion = "121.5.6";
    final StandardDestinationDefinition destination = generateDestinationDefinition();
    destination.getSpec().setProtocolVersion(invalidProtocolVersion);
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());

    when(uuidSupplier.get()).thenReturn(destination.getDestinationDefinitionId());
    when(schedulerSynchronousClient.createGetSpecJob(imageName)).thenReturn(new SynchronousResponse<>(
        destination.getSpec(),
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final DestinationDefinitionCreate create = new DestinationDefinitionCreate()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .icon(destination.getIcon())
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    assertThrows(UnsupportedProtocolVersionException.class, () -> destinationDefinitionsHandler.createPrivateDestinationDefinition(create));

    verify(schedulerSynchronousClient).createGetSpecJob(imageName);
    verify(configRepository, never()).writeStandardDestinationDefinition(destination
        .withProtocolVersion(DEFAULT_PROTOCOL_VERSION)
        .withReleaseDate(null)
        .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM));
  }

  @Test
  @DisplayName("createCustomDestinationDefinition should correctly create a destinationDefinition")
  void testCreateCustomDestinationDefinition() throws URISyntaxException, IOException, JsonValidationException {
    final StandardDestinationDefinition destination = generateDestinationDefinition();
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());

    when(uuidSupplier.get()).thenReturn(destination.getDestinationDefinitionId());
    when(schedulerSynchronousClient.createGetSpecJob(imageName)).thenReturn(new SynchronousResponse<>(
        destination.getSpec(),
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final DestinationDefinitionCreate create = new DestinationDefinitionCreate()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .icon(destination.getIcon())
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final CustomDestinationDefinitionCreate customCreate = new CustomDestinationDefinitionCreate()
        .destinationDefinition(create)
        .workspaceId(workspaceId);

    final DestinationDefinitionRead expectedRead = new DestinationDefinitionRead()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .destinationDefinitionId(destination.getDestinationDefinitionId())
        .icon(DestinationDefinitionsHandler.loadIcon(destination.getIcon()))
        .protocolVersion(DEFAULT_PROTOCOL_VERSION)
        .releaseStage(ReleaseStage.CUSTOM)
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final DestinationDefinitionRead actualRead = destinationDefinitionsHandler.createCustomDestinationDefinition(customCreate);

    assertEquals(expectedRead, actualRead);
    verify(schedulerSynchronousClient).createGetSpecJob(imageName);
    verify(configRepository).writeCustomDestinationDefinition(
        destination
            .withProtocolVersion(DEFAULT_PROTOCOL_VERSION)
            .withReleaseDate(null)
            .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM)
            .withCustom(true),
        workspaceId);
  }

  @Test
  @DisplayName("createCustomDestinationDefinition should not create a destinationDefinition with unsupported protocol range")
  void testCreateCustomDestinationDefinitionWithInvalidProtocol() throws URISyntaxException, IOException, JsonValidationException {
    final String invalidProtocol = "122.1.22";
    final StandardDestinationDefinition destination = generateDestinationDefinition();
    destination.getSpec().setProtocolVersion(invalidProtocol);
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());

    when(uuidSupplier.get()).thenReturn(destination.getDestinationDefinitionId());
    when(schedulerSynchronousClient.createGetSpecJob(imageName)).thenReturn(new SynchronousResponse<>(
        destination.getSpec(),
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final DestinationDefinitionCreate create = new DestinationDefinitionCreate()
        .name(destination.getName())
        .dockerRepository(destination.getDockerRepository())
        .dockerImageTag(destination.getDockerImageTag())
        .documentationUrl(new URI(destination.getDocumentationUrl()))
        .icon(destination.getIcon())
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destination.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final CustomDestinationDefinitionCreate customCreate = new CustomDestinationDefinitionCreate()
        .destinationDefinition(create)
        .workspaceId(workspaceId);

    assertThrows(UnsupportedProtocolVersionException.class, () -> destinationDefinitionsHandler.createCustomDestinationDefinition(customCreate));

    verify(schedulerSynchronousClient).createGetSpecJob(imageName);
    verify(configRepository, never()).writeCustomDestinationDefinition(
        destination
            .withProtocolVersion(invalidProtocol)
            .withReleaseDate(null)
            .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM)
            .withCustom(true),
        workspaceId);
  }

  @Test
  @DisplayName("updateDestinationDefinition should correctly update a destinationDefinition")
  void testUpdateDestination() throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId())).thenReturn(destinationDefinition);
    final DestinationDefinitionRead currentDestination = destinationDefinitionsHandler
        .getDestinationDefinition(
            new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationDefinition.getDestinationDefinitionId()));
    final String currentTag = currentDestination.getDockerImageTag();
    final String newDockerImageTag = "averydifferenttag";
    final String newProtocolVersion = "0.2.4";
    assertNotEquals(newDockerImageTag, currentTag);
    assertNotEquals(newProtocolVersion, currentDestination.getProtocolVersion());

    final String newImageName = DockerUtils.getTaggedImageName(destinationDefinition.getDockerRepository(), newDockerImageTag);
    final ConnectorSpecification newSpec = new ConnectorSpecification()
        .withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo2", "bar2")))
        .withProtocolVersion(newProtocolVersion);
    when(schedulerSynchronousClient.createGetSpecJob(newImageName)).thenReturn(new SynchronousResponse<>(
        newSpec,
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final StandardDestinationDefinition updatedDestination =
        Jsons.clone(destinationDefinition).withDockerImageTag(newDockerImageTag).withSpec(newSpec).withProtocolVersion(newProtocolVersion);

    final DestinationDefinitionRead destinationRead = destinationDefinitionsHandler.updateDestinationDefinition(
        new DestinationDefinitionUpdate().destinationDefinitionId(this.destinationDefinition.getDestinationDefinitionId())
            .dockerImageTag(newDockerImageTag));

    assertEquals(newDockerImageTag, destinationRead.getDockerImageTag());
    verify(schedulerSynchronousClient).createGetSpecJob(newImageName);
    verify(configRepository).writeStandardDestinationDefinition(updatedDestination);

    final Configs configs = new EnvConfigs();
    final AirbyteProtocolVersionRange protocolVersionRange =
        new AirbyteProtocolVersionRange(configs.getAirbyteProtocolVersionMin(), configs.getAirbyteProtocolVersionMax());
    verify(configRepository).clearUnsupportedProtocolVersionFlag(updatedDestination.getDestinationDefinitionId(), ActorType.DESTINATION,
        protocolVersionRange);
  }

  @Test
  @DisplayName("updateDestinationDefinition should not update a destinationDefinition if protocol version is out of range")
  void testOutOfProtocolRangeUpdateDestination() throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId())).thenReturn(destinationDefinition);
    final DestinationDefinitionRead currentDestination = destinationDefinitionsHandler
        .getDestinationDefinition(
            new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationDefinition.getDestinationDefinitionId()));
    final String currentTag = currentDestination.getDockerImageTag();
    final String newDockerImageTag = "averydifferenttagforprotocolversion";
    final String newProtocolVersion = "120.2.4";
    assertNotEquals(newDockerImageTag, currentTag);
    assertNotEquals(newProtocolVersion, currentDestination.getProtocolVersion());

    final String newImageName = DockerUtils.getTaggedImageName(destinationDefinition.getDockerRepository(), newDockerImageTag);
    final ConnectorSpecification newSpec = new ConnectorSpecification()
        .withConnectionSpecification(Jsons.jsonNode(ImmutableMap.of("foo2", "bar2")))
        .withProtocolVersion(newProtocolVersion);
    when(schedulerSynchronousClient.createGetSpecJob(newImageName)).thenReturn(new SynchronousResponse<>(
        newSpec,
        SynchronousJobMetadata.mock(ConfigType.GET_SPEC)));

    final StandardDestinationDefinition updatedDestination =
        Jsons.clone(destinationDefinition).withDockerImageTag(newDockerImageTag).withSpec(newSpec).withProtocolVersion(newProtocolVersion);

    assertThrows(UnsupportedProtocolVersionException.class, () -> destinationDefinitionsHandler.updateDestinationDefinition(
        new DestinationDefinitionUpdate().destinationDefinitionId(this.destinationDefinition.getDestinationDefinitionId())
            .dockerImageTag(newDockerImageTag)));

    verify(schedulerSynchronousClient).createGetSpecJob(newImageName);
    verify(configRepository, never()).writeStandardDestinationDefinition(updatedDestination);
  }

  @Test
  @DisplayName("deleteDestinationDefinition should correctly delete a sourceDefinition")
  void testDeleteDestinationDefinition() throws ConfigNotFoundException, IOException, JsonValidationException {
    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody =
        new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationDefinition.getDestinationDefinitionId());
    final StandardDestinationDefinition updatedDestinationDefinition = Jsons.clone(this.destinationDefinition).withTombstone(true);
    final DestinationRead destination = new DestinationRead();

    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);
    when(destinationHandler.listDestinationsForDestinationDefinition(destinationDefinitionIdRequestBody))
        .thenReturn(new DestinationReadList().destinations(Collections.singletonList(destination)));

    assertFalse(destinationDefinition.getTombstone());

    destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);

    verify(destinationHandler).deleteDestination(destination);
    verify(configRepository).writeStandardDestinationDefinition(updatedDestinationDefinition);
  }

  @Test
  @DisplayName("grantDestinationDefinitionToWorkspace should correctly create a workspace grant")
  void testGrantDestinationDefinitionToWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.getStandardDestinationDefinition(destinationDefinition.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);

    final DestinationDefinitionRead expectedDestinationDefinitionRead = new DestinationDefinitionRead()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .name(destinationDefinition.getName())
        .dockerRepository(destinationDefinition.getDockerRepository())
        .dockerImageTag(destinationDefinition.getDockerImageTag())
        .documentationUrl(new URI(destinationDefinition.getDocumentationUrl()))
        .icon(DestinationDefinitionsHandler.loadIcon(destinationDefinition.getIcon()))
        .protocolVersion(destinationDefinition.getProtocolVersion())
        .releaseStage(ReleaseStage.fromValue(destinationDefinition.getReleaseStage().value()))
        .releaseDate(LocalDate.parse(destinationDefinition.getReleaseDate()))
        .resourceRequirements(new io.airbyte.api.model.generated.ActorDefinitionResourceRequirements()
            ._default(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(destinationDefinition.getResourceRequirements().getDefault().getCpuRequest()))
            .jobSpecific(Collections.emptyList()));

    final PrivateDestinationDefinitionRead expectedPrivateDestinationDefinitionRead =
        new PrivateDestinationDefinitionRead().destinationDefinition(expectedDestinationDefinitionRead).granted(true);

    final PrivateDestinationDefinitionRead actualPrivateDestinationDefinitionRead =
        destinationDefinitionsHandler.grantDestinationDefinitionToWorkspace(
            new DestinationDefinitionIdWithWorkspaceId()
                .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
                .workspaceId(workspaceId));

    assertEquals(expectedPrivateDestinationDefinitionRead, actualPrivateDestinationDefinitionRead);
    verify(configRepository).writeActorDefinitionWorkspaceGrant(
        destinationDefinition.getDestinationDefinitionId(),
        workspaceId);
  }

  @Test
  @DisplayName("revokeDestinationDefinitionFromWorkspace should correctly delete a workspace grant")
  void testRevokeDestinationDefinitionFromWorkspace() throws IOException {
    destinationDefinitionsHandler.revokeDestinationDefinitionFromWorkspace(new DestinationDefinitionIdWithWorkspaceId()
        .destinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
        .workspaceId(workspaceId));
    verify(configRepository).deleteActorDefinitionWorkspaceGrant(
        destinationDefinition.getDestinationDefinitionId(),
        workspaceId);
  }

  @Nested
  @DisplayName("listLatest")
  class listLatest {

    @Test
    @DisplayName("should return the latest list")
    void testCorrect() throws InterruptedException {
      final StandardDestinationDefinition destinationDefinition = generateDestinationDefinition();
      when(githubStore.getLatestDestinations()).thenReturn(Collections.singletonList(destinationDefinition));

      final var destinationDefinitionReadList = destinationDefinitionsHandler.listLatestDestinationDefinitions().getDestinationDefinitions();
      assertEquals(1, destinationDefinitionReadList.size());

      final var destinationDefinitionRead = destinationDefinitionReadList.get(0);
      assertEquals(DestinationDefinitionsHandler.buildDestinationDefinitionRead(destinationDefinition), destinationDefinitionRead);
    }

    @Test
    @DisplayName("returns empty collection if cannot find latest definitions")
    void testHttpTimeout() {
      assertEquals(0, destinationDefinitionsHandler.listLatestDestinationDefinitions().getDestinationDefinitions().size());
    }

  }

}
