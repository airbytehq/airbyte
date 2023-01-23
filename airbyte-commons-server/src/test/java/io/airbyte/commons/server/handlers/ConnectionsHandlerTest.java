/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static io.airbyte.commons.server.helpers.ConnectionHelpers.FIELD_NAME;
import static io.airbyte.commons.server.helpers.ConnectionHelpers.SECOND_FIELD_NAME;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.AirbyteCatalog;
import io.airbyte.api.model.generated.AirbyteStream;
import io.airbyte.api.model.generated.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.generated.AirbyteStreamConfiguration;
import io.airbyte.api.model.generated.ConnectionCreate;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionReadList;
import io.airbyte.api.model.generated.ConnectionSchedule;
import io.airbyte.api.model.generated.ConnectionScheduleData;
import io.airbyte.api.model.generated.ConnectionScheduleDataBasicSchedule;
import io.airbyte.api.model.generated.ConnectionScheduleDataBasicSchedule.TimeUnitEnum;
import io.airbyte.api.model.generated.ConnectionScheduleDataCron;
import io.airbyte.api.model.generated.ConnectionScheduleType;
import io.airbyte.api.model.generated.ConnectionSearch;
import io.airbyte.api.model.generated.ConnectionStatus;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.DestinationSearch;
import io.airbyte.api.model.generated.DestinationSyncMode;
import io.airbyte.api.model.generated.NamespaceDefinitionType;
import io.airbyte.api.model.generated.ResourceRequirements;
import io.airbyte.api.model.generated.SelectedFieldInfo;
import io.airbyte.api.model.generated.SourceSearch;
import io.airbyte.api.model.generated.StreamDescriptor;
import io.airbyte.api.model.generated.SyncMode;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.converters.ApiPojoConverters;
import io.airbyte.commons.server.handlers.helpers.CatalogConverter;
import io.airbyte.commons.server.helpers.ConnectionHelpers;
import io.airbyte.commons.server.scheduler.EventRunner;
import io.airbyte.config.BasicSchedule;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Cron;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.FieldSelectionData;
import io.airbyte.config.Geography;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.Schedule;
import io.airbyte.config.Schedule.TimeUnit;
import io.airbyte.config.ScheduleData;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.ScheduleType;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.helper.ConnectionHelper;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import org.assertj.core.api.Assertions;
import org.junit.Assert;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class ConnectionsHandlerTest {

  private ConfigRepository configRepository;
  private Supplier<UUID> uuidGenerator;

  private ConnectionsHandler connectionsHandler;
  private UUID workspaceId;
  private UUID sourceId;
  private UUID destinationId;

  private SourceConnection source;
  private DestinationConnection destination;
  private StandardSync standardSync;
  private StandardSync standardSyncDeleted;
  private UUID connectionId;
  private UUID operationId;
  private UUID otherOperationId;
  private WorkspaceHelper workspaceHelper;
  private TrackingClient trackingClient;
  private EventRunner eventRunner;
  private ConnectionHelper connectionHelper;

  private static final String PRESTO_TO_HUDI = "presto to hudi";
  private static final String PRESTO_TO_HUDI_PREFIX = "presto_to_hudi";
  private static final String SOURCE_TEST = "source-test";
  private static final String DESTINATION_TEST = "destination-test";
  private static final String CURSOR1 = "cursor1";
  private static final String CURSOR2 = "cursor2";
  private static final String PK1 = "pk1";
  private static final String PK2 = "pk2";
  private static final String PK3 = "pk3";
  private static final String STREAM1 = "stream1";
  private static final String STREAM2 = "stream2";
  private static final String AZKABAN_USERS = "azkaban_users";
  private final static String CRON_TIMEZONE_UTC = "UTC";
  private final static String CRON_EXPRESSION = "* */2 * * * ?";

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException, JsonValidationException, ConfigNotFoundException {

    workspaceId = UUID.randomUUID();
    sourceId = UUID.randomUUID();
    destinationId = UUID.randomUUID();
    connectionId = UUID.randomUUID();
    operationId = UUID.randomUUID();
    otherOperationId = UUID.randomUUID();
    source = new SourceConnection()
        .withSourceId(sourceId)
        .withWorkspaceId(workspaceId)
        .withName("presto");
    destination = new DestinationConnection()
        .withDestinationId(destinationId)
        .withWorkspaceId(workspaceId)
        .withName("hudi")
        .withConfiguration(Jsons.jsonNode(Collections.singletonMap("apiKey", "123-abc")));
    standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withName(PRESTO_TO_HUDI)
        .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix(PRESTO_TO_HUDI_PREFIX)
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog())
        .withFieldSelectionData(new FieldSelectionData().withAdditionalProperty("null/users-data0", false))
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId))
        .withManual(false)
        .withSchedule(ConnectionHelpers.generateBasicSchedule())
        .withScheduleType(ScheduleType.BASIC_SCHEDULE)
        .withScheduleData(ConnectionHelpers.generateBasicScheduleData())
        .withResourceRequirements(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS)
        .withSourceCatalogId(UUID.randomUUID())
        .withGeography(Geography.AUTO)
        .withBreakingChange(false);
    standardSyncDeleted = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi2")
        .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi2")
        .withStatus(StandardSync.Status.DEPRECATED)
        .withCatalog(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog())
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId))
        .withManual(false)
        .withSchedule(ConnectionHelpers.generateBasicSchedule())
        .withResourceRequirements(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS)
        .withGeography(Geography.US);

    configRepository = mock(ConfigRepository.class);
    uuidGenerator = mock(Supplier.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    trackingClient = mock(TrackingClient.class);
    eventRunner = mock(EventRunner.class);
    connectionHelper = mock(ConnectionHelper.class);
    when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(sourceId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(otherOperationId)).thenReturn(workspaceId);
  }

  @Nested
  class UnMockedConnectionHelper {

    @BeforeEach
    void setUp() throws JsonValidationException, ConfigNotFoundException, IOException {
      connectionsHandler = new ConnectionsHandler(
          configRepository,
          uuidGenerator,
          workspaceHelper,
          trackingClient,
          eventRunner,
          connectionHelper);

      when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
      final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
          .withName(SOURCE_TEST)
          .withSourceDefinitionId(UUID.randomUUID());
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withName(DESTINATION_TEST)
          .withDestinationDefinitionId(UUID.randomUUID());
      when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
      when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(
          sourceDefinition);
      when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(
          destinationDefinition);
      when(configRepository.getSourceConnection(source.getSourceId()))
          .thenReturn(source);
      when(configRepository.getDestinationConnection(destination.getDestinationId()))
          .thenReturn(destination);
    }

    @Nested
    class CreateConnection {

      private ConnectionCreate buildConnectionCreateRequest(final StandardSync standardSync, final AirbyteCatalog catalog) {
        return new ConnectionCreate()
            .sourceId(standardSync.getSourceId())
            .destinationId(standardSync.getDestinationId())
            .operationIds(standardSync.getOperationIds())
            .name(PRESTO_TO_HUDI)
            .namespaceDefinition(NamespaceDefinitionType.SOURCE)
            .namespaceFormat(null)
            .prefix(PRESTO_TO_HUDI_PREFIX)
            .status(ConnectionStatus.ACTIVE)
            .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
            .syncCatalog(catalog)
            .resourceRequirements(new io.airbyte.api.model.generated.ResourceRequirements()
                .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
                .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
                .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest())
                .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit()))
            .sourceCatalogId(standardSync.getSourceCatalogId())
            .geography(ApiPojoConverters.toApiGeography(standardSync.getGeography()));
      }

      @Test
      void testCreateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {

        final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

        // set a defaultGeography on the workspace as EU, but expect connection to be
        // created AUTO because the ConnectionCreate geography takes precedence over the workspace
        // defaultGeography.
        final StandardWorkspace workspace = new StandardWorkspace()
            .withWorkspaceId(workspaceId)
            .withDefaultGeography(Geography.EU);
        when(configRepository.getStandardWorkspaceNoSecrets(workspaceId, true)).thenReturn(workspace);

        final ConnectionCreate connectionCreate = buildConnectionCreateRequest(standardSync, catalog);

        final ConnectionRead actualConnectionRead = connectionsHandler.createConnection(connectionCreate);

        final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

        assertEquals(expectedConnectionRead, actualConnectionRead);

        verify(configRepository).writeStandardSync(standardSync);

        // Use new schedule schema, verify that we get the same results.
        connectionCreate
            .schedule(null)
            .scheduleType(ConnectionScheduleType.BASIC)
            .scheduleData(ConnectionHelpers.generateBasicConnectionScheduleData());
        assertEquals(expectedConnectionRead, connectionsHandler.createConnection(connectionCreate));
      }

      @Test
      void testCreateConnectionUsesDefaultGeographyFromWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {

        when(workspaceHelper.getWorkspaceForSourceId(sourceId)).thenReturn(workspaceId);

        final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

        // don't set a geography on the ConnectionCreate to force inheritance from workspace default
        final ConnectionCreate connectionCreate = buildConnectionCreateRequest(standardSync, catalog).geography(null);

        // set the workspace default to EU
        final StandardWorkspace workspace = new StandardWorkspace()
            .withWorkspaceId(workspaceId)
            .withDefaultGeography(Geography.EU);
        when(configRepository.getStandardWorkspaceNoSecrets(workspaceId, true)).thenReturn(workspace);

        // the expected read and verified write is generated from the standardSync, so set this to EU as
        // well
        standardSync.setGeography(Geography.EU);

        final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);
        final ConnectionRead actualConnectionRead = connectionsHandler.createConnection(connectionCreate);

        assertEquals(expectedConnectionRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(standardSync);
      }

      @Test
      void testCreateConnectionWithSelectedFields() throws IOException, JsonValidationException, ConfigNotFoundException {
        final StandardWorkspace workspace = new StandardWorkspace()
            .withWorkspaceId(workspaceId)
            .withDefaultGeography(Geography.AUTO);
        when(configRepository.getStandardWorkspaceNoSecrets(workspaceId, true)).thenReturn(workspace);

        final AirbyteCatalog catalogWithSelectedFields = ConnectionHelpers.generateApiCatalogWithTwoFields();
        // Only select one of the two fields.
        catalogWithSelectedFields.getStreams().get(0).getConfig().fieldSelectionEnabled(true)
            .selectedFields(List.of(new SelectedFieldInfo().addFieldPathItem(FIELD_NAME)));

        final ConnectionCreate connectionCreate = buildConnectionCreateRequest(standardSync, catalogWithSelectedFields);

        final ConnectionRead actualConnectionRead = connectionsHandler.createConnection(connectionCreate);

        final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

        assertEquals(expectedConnectionRead, actualConnectionRead);

        standardSync.withFieldSelectionData(new FieldSelectionData().withAdditionalProperty("null/users-data0", true));

        verify(configRepository).writeStandardSync(standardSync);
      }

      @Test
      void testCreateFullRefreshConnectionWithSelectedFields() throws IOException, JsonValidationException, ConfigNotFoundException {
        final StandardWorkspace workspace = new StandardWorkspace()
            .withWorkspaceId(workspaceId)
            .withDefaultGeography(Geography.AUTO);
        when(configRepository.getStandardWorkspaceNoSecrets(workspaceId, true)).thenReturn(workspace);

        final AirbyteCatalog fullRefreshCatalogWithSelectedFields = ConnectionHelpers.generateApiCatalogWithTwoFields();
        fullRefreshCatalogWithSelectedFields.getStreams().get(0).getConfig()
            .fieldSelectionEnabled(true)
            .selectedFields(List.of(new SelectedFieldInfo().addFieldPathItem(FIELD_NAME)))
            .cursorField(null)
            .syncMode(SyncMode.FULL_REFRESH);

        final ConnectionCreate connectionCreate = buildConnectionCreateRequest(standardSync, fullRefreshCatalogWithSelectedFields);

        final ConnectionRead actualConnectionRead = connectionsHandler.createConnection(connectionCreate);

        final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

        assertEquals(expectedConnectionRead, actualConnectionRead);

        standardSync
            .withFieldSelectionData(new FieldSelectionData().withAdditionalProperty("null/users-data0", true))
            .getCatalog().getStreams().get(0).withSyncMode(io.airbyte.protocol.models.SyncMode.FULL_REFRESH).withCursorField(null);

        verify(configRepository).writeStandardSync(standardSync);
      }

      @Test
      void testFieldSelectionRemoveCursorFails() throws JsonValidationException, ConfigNotFoundException, IOException {
        // Test that if we try to de-select a field that's being used for the cursor, the request will fail.
        // The connection initially has a catalog with one stream, and two fields in that stream.
        standardSync.setCatalog(ConnectionHelpers.generateAirbyteCatalogWithTwoFields());

        // Send an update that sets a cursor but de-selects that field.
        final AirbyteCatalog catalogForUpdate = ConnectionHelpers.generateApiCatalogWithTwoFields();
        catalogForUpdate.getStreams().get(0).getConfig()
            .fieldSelectionEnabled(true)
            .selectedFields(List.of(new SelectedFieldInfo().addFieldPathItem(FIELD_NAME)))
            .cursorField(List.of(SECOND_FIELD_NAME))
            .syncMode(SyncMode.INCREMENTAL);

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .syncCatalog(catalogForUpdate);

        assertThrows(JsonValidationException.class, () -> connectionsHandler.updateConnection(connectionUpdate));
      }

      @Test
      void testFieldSelectionRemovePrimaryKeyFails() throws JsonValidationException, ConfigNotFoundException, IOException {
        // Test that if we try to de-select a field that's being used for the primary key, the request will
        // fail.
        // The connection initially has a catalog with one stream, and two fields in that stream.
        standardSync.setCatalog(ConnectionHelpers.generateAirbyteCatalogWithTwoFields());

        // Send an update that sets a primary key but deselects that field.
        final AirbyteCatalog catalogForUpdate = ConnectionHelpers.generateApiCatalogWithTwoFields();
        catalogForUpdate.getStreams().get(0).getConfig()
            .fieldSelectionEnabled(true)
            .selectedFields(List.of(new SelectedFieldInfo().addFieldPathItem(FIELD_NAME)))
            .destinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .primaryKey(List.of(List.of(SECOND_FIELD_NAME)));

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .syncCatalog(catalogForUpdate);

        assertThrows(JsonValidationException.class, () -> connectionsHandler.updateConnection(connectionUpdate));
      }

      @Test
      void testValidateConnectionCreateSourceAndDestinationInDifferenceWorkspace() {

        when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationId)).thenReturn(UUID.randomUUID());

        final ConnectionCreate connectionCreate = new ConnectionCreate()
            .sourceId(standardSync.getSourceId())
            .destinationId(standardSync.getDestinationId());

        assertThrows(IllegalArgumentException.class, () -> connectionsHandler.createConnection(connectionCreate));
      }

      @Test
      void testValidateConnectionCreateOperationInDifferentWorkspace() {

        when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(UUID.randomUUID());

        final ConnectionCreate connectionCreate = new ConnectionCreate()
            .sourceId(standardSync.getSourceId())
            .destinationId(standardSync.getDestinationId())
            .operationIds(Collections.singletonList(operationId));

        assertThrows(IllegalArgumentException.class, () -> connectionsHandler.createConnection(connectionCreate));
      }

      @Test
      void testCreateConnectionWithBadDefinitionIds() throws JsonValidationException, ConfigNotFoundException, IOException {

        final UUID sourceIdBad = UUID.randomUUID();
        final UUID destinationIdBad = UUID.randomUUID();

        when(configRepository.getSourceConnection(sourceIdBad))
            .thenThrow(new ConfigNotFoundException(ConfigSchema.SOURCE_CONNECTION, sourceIdBad));
        when(configRepository.getDestinationConnection(destinationIdBad))
            .thenThrow(new ConfigNotFoundException(ConfigSchema.DESTINATION_CONNECTION, destinationIdBad));

        final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

        final ConnectionCreate connectionCreateBadSource = new ConnectionCreate()
            .sourceId(sourceIdBad)
            .destinationId(standardSync.getDestinationId())
            .operationIds(standardSync.getOperationIds())
            .name(PRESTO_TO_HUDI)
            .namespaceDefinition(NamespaceDefinitionType.SOURCE)
            .namespaceFormat(null)
            .prefix(PRESTO_TO_HUDI_PREFIX)
            .status(ConnectionStatus.ACTIVE)
            .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
            .syncCatalog(catalog);

        assertThrows(ConfigNotFoundException.class, () -> connectionsHandler.createConnection(connectionCreateBadSource));

        final ConnectionCreate connectionCreateBadDestination = new ConnectionCreate()
            .sourceId(standardSync.getSourceId())
            .destinationId(destinationIdBad)
            .operationIds(standardSync.getOperationIds())
            .name(PRESTO_TO_HUDI)
            .namespaceDefinition(NamespaceDefinitionType.SOURCE)
            .namespaceFormat(null)
            .prefix(PRESTO_TO_HUDI_PREFIX)
            .status(ConnectionStatus.ACTIVE)
            .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
            .syncCatalog(catalog);

        assertThrows(ConfigNotFoundException.class, () -> connectionsHandler.createConnection(connectionCreateBadDestination));

      }

    }

    @Nested
    class UpdateConnection {

      @Test
      void testUpdateConnectionPatchSingleField() throws Exception {
        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .name("newName");

        final ConnectionRead expectedRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync)
            .name("newName");
        final StandardSync expectedPersistedSync = Jsons.clone(standardSync).withName("newName");

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        assertEquals(expectedRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testUpdateConnectionPatchScheduleToManual() throws Exception {
        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .scheduleType(ConnectionScheduleType.MANUAL);

        final ConnectionRead expectedRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync)
            .schedule(null)
            .scheduleType(ConnectionScheduleType.MANUAL)
            .scheduleData(null);

        final StandardSync expectedPersistedSync = Jsons.clone(standardSync)
            .withSchedule(null)
            .withScheduleType(ScheduleType.MANUAL)
            .withScheduleData(null)
            .withManual(true);

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        assertEquals(expectedRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testUpdateConnectionPatchScheduleToCron() throws Exception {

        final ConnectionScheduleData cronScheduleData = new ConnectionScheduleData().cron(
            new ConnectionScheduleDataCron().cronExpression(CRON_EXPRESSION).cronTimeZone(CRON_TIMEZONE_UTC));

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .scheduleType(ConnectionScheduleType.CRON)
            .scheduleData(cronScheduleData);

        final ConnectionRead expectedRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync)
            .schedule(null)
            .scheduleType(ConnectionScheduleType.CRON)
            .scheduleData(cronScheduleData);

        final StandardSync expectedPersistedSync = Jsons.clone(standardSync)
            .withSchedule(null)
            .withScheduleType(ScheduleType.CRON)
            .withScheduleData(new ScheduleData().withCron(new Cron().withCronExpression(CRON_EXPRESSION).withCronTimeZone(CRON_TIMEZONE_UTC)))
            .withManual(false);

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        assertEquals(expectedRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testUpdateConnectionPatchBasicSchedule() throws Exception {

        final ConnectionScheduleData newScheduleData =
            new ConnectionScheduleData().basicSchedule(new ConnectionScheduleDataBasicSchedule().timeUnit(TimeUnitEnum.DAYS).units(10L));

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .scheduleType(ConnectionScheduleType.BASIC) // update route requires this to be set even if it isn't changing
            .scheduleData(newScheduleData);

        final ConnectionRead expectedRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync)
            .schedule(new ConnectionSchedule().timeUnit(ConnectionSchedule.TimeUnitEnum.DAYS).units(10L)) // still dual-writing to legacy field
            .scheduleType(ConnectionScheduleType.BASIC)
            .scheduleData(newScheduleData);

        final StandardSync expectedPersistedSync = Jsons.clone(standardSync)
            .withSchedule(new Schedule().withTimeUnit(TimeUnit.DAYS).withUnits(10L)) // still dual-writing to legacy field
            .withScheduleType(ScheduleType.BASIC_SCHEDULE)
            .withScheduleData(new ScheduleData().withBasicSchedule(new BasicSchedule().withTimeUnit(BasicSchedule.TimeUnit.DAYS).withUnits(10L)))
            .withManual(false);

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        assertEquals(expectedRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testUpdateConnectionPatchAddingNewStream() throws Exception {
        // the connection initially has a catalog with one stream. this test generates another catalog with
        // one stream, changes that stream's name to something new, and sends both streams in the patch
        // request.
        // the test expects the final result to include both streams.
        final AirbyteCatalog catalogWithNewStream = ConnectionHelpers.generateBasicApiCatalog();
        catalogWithNewStream.getStreams().get(0).getStream().setName(AZKABAN_USERS);
        catalogWithNewStream.getStreams().get(0).getConfig().setAliasName(AZKABAN_USERS);

        final AirbyteCatalog catalogForUpdate = ConnectionHelpers.generateMultipleStreamsApiCatalog(2);
        catalogForUpdate.getStreams().get(1).getStream().setName(AZKABAN_USERS);
        catalogForUpdate.getStreams().get(1).getConfig().setAliasName(AZKABAN_USERS);

        // expect two streams in the final persisted catalog -- the original unchanged stream, plus the new
        // AZKABAN_USERS stream

        final ConfiguredAirbyteCatalog expectedPersistedCatalog = ConnectionHelpers.generateMultipleStreamsConfiguredAirbyteCatalog(2);
        expectedPersistedCatalog.getStreams().get(1).getStream().setName(AZKABAN_USERS);

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .syncCatalog(catalogForUpdate);

        final ConnectionRead expectedRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync)
            .syncCatalog(catalogForUpdate);

        final StandardSync expectedPersistedSync = Jsons.clone(standardSync)
            .withCatalog(expectedPersistedCatalog)
            .withFieldSelectionData(CatalogConverter.getFieldSelectionData(catalogForUpdate));

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        assertEquals(expectedRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testUpdateConnectionPatchEditExistingStreamWhileAddingNewStream() throws Exception {
        // the connection initially has a catalog with two streams. this test updates the catalog
        // with a sync mode change for one of the initial streams while also adding a brand-new
        // stream. The result should be a catalog with three streams.
        standardSync.setCatalog(ConnectionHelpers.generateMultipleStreamsConfiguredAirbyteCatalog(2));

        final AirbyteCatalog catalogForUpdate = ConnectionHelpers.generateMultipleStreamsApiCatalog(3);
        catalogForUpdate.getStreams().get(0).getConfig().setSyncMode(SyncMode.FULL_REFRESH);
        catalogForUpdate.getStreams().get(2).getStream().setName(AZKABAN_USERS);
        catalogForUpdate.getStreams().get(2).getConfig().setAliasName(AZKABAN_USERS);

        // expect three streams in the final persisted catalog
        final ConfiguredAirbyteCatalog expectedPersistedCatalog = ConnectionHelpers.generateMultipleStreamsConfiguredAirbyteCatalog(3);
        expectedPersistedCatalog.getStreams().get(0).withSyncMode(io.airbyte.protocol.models.SyncMode.FULL_REFRESH);
        // index 1 is unchanged
        expectedPersistedCatalog.getStreams().get(2).getStream().withName(AZKABAN_USERS);

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .syncCatalog(catalogForUpdate);

        final ConnectionRead expectedRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync)
            .syncCatalog(catalogForUpdate);

        final StandardSync expectedPersistedSync = Jsons.clone(standardSync)
            .withCatalog(expectedPersistedCatalog)
            .withFieldSelectionData(CatalogConverter.getFieldSelectionData(catalogForUpdate));

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        assertEquals(expectedRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testUpdateConnectionPatchColumnSelection() throws Exception {
        // The connection initially has a catalog with one stream, and two fields in that stream.
        standardSync.setCatalog(ConnectionHelpers.generateAirbyteCatalogWithTwoFields());

        // Send an update that only selects one of the fields.
        final AirbyteCatalog catalogForUpdate = ConnectionHelpers.generateApiCatalogWithTwoFields();
        catalogForUpdate.getStreams().get(0).getConfig().fieldSelectionEnabled(true)
            .selectedFields(List.of(new SelectedFieldInfo().addFieldPathItem(FIELD_NAME)));

        // Expect one column in the final persisted catalog
        final ConfiguredAirbyteCatalog expectedPersistedCatalog = ConnectionHelpers.generateBasicConfiguredAirbyteCatalog();

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .syncCatalog(catalogForUpdate);

        final ConnectionRead expectedRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync)
            .syncCatalog(catalogForUpdate);

        final StandardSync expectedPersistedSync = Jsons.clone(standardSync)
            .withCatalog(expectedPersistedCatalog)
            .withFieldSelectionData(CatalogConverter.getFieldSelectionData(catalogForUpdate));

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        assertEquals(expectedRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testUpdateConnectionPatchingSeveralFieldsAndReplaceAStream() throws JsonValidationException, ConfigNotFoundException, IOException {
        final AirbyteCatalog catalogForUpdate = ConnectionHelpers.generateMultipleStreamsApiCatalog(2);

        // deselect the existing stream, and add a new stream called 'azkaban_users'.
        // result that we persist and read after update should be a catalog with a single
        // stream called 'azkaban_users'.
        catalogForUpdate.getStreams().get(0).getConfig().setSelected(false);
        catalogForUpdate.getStreams().get(1).getStream().setName(AZKABAN_USERS);
        catalogForUpdate.getStreams().get(1).getConfig().setAliasName(AZKABAN_USERS);

        final UUID newSourceCatalogId = UUID.randomUUID();

        final ResourceRequirements resourceRequirements = new ResourceRequirements()
            .cpuLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuLimit())
            .cpuRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuRequest())
            .memoryLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryLimit())
            .memoryRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryRequest());

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .status(ConnectionStatus.INACTIVE)
            .scheduleType(ConnectionScheduleType.MANUAL)
            .syncCatalog(catalogForUpdate)
            .resourceRequirements(resourceRequirements)
            .sourceCatalogId(newSourceCatalogId)
            .operationIds(List.of(operationId, otherOperationId))
            .geography(io.airbyte.api.model.generated.Geography.EU);

        final ConfiguredAirbyteCatalog expectedPersistedCatalog = ConnectionHelpers.generateBasicConfiguredAirbyteCatalog();
        expectedPersistedCatalog.getStreams().get(0).getStream().withName(AZKABAN_USERS);

        final StandardSync expectedPersistedSync = Jsons.clone(standardSync)
            .withStatus(Status.INACTIVE)
            .withScheduleType(ScheduleType.MANUAL)
            .withScheduleData(null)
            .withSchedule(null)
            .withManual(true)
            .withCatalog(expectedPersistedCatalog)
            .withFieldSelectionData(CatalogConverter.getFieldSelectionData(catalogForUpdate))
            .withResourceRequirements(ApiPojoConverters.resourceRequirementsToInternal(resourceRequirements))
            .withSourceCatalogId(newSourceCatalogId)
            .withOperationIds(List.of(operationId, otherOperationId))
            .withGeography(Geography.EU);

        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

        final AirbyteCatalog expectedCatalogInRead = ConnectionHelpers.generateBasicApiCatalog();
        expectedCatalogInRead.getStreams().get(0).getStream().setName(AZKABAN_USERS);
        expectedCatalogInRead.getStreams().get(0).getConfig().setAliasName(AZKABAN_USERS);

        final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(
            standardSync.getConnectionId(),
            standardSync.getSourceId(),
            standardSync.getDestinationId(),
            standardSync.getOperationIds(),
            newSourceCatalogId,
            ApiPojoConverters.toApiGeography(standardSync.getGeography()), false)
            .status(ConnectionStatus.INACTIVE)
            .scheduleType(ConnectionScheduleType.MANUAL)
            .scheduleData(null)
            .schedule(null)
            .syncCatalog(expectedCatalogInRead)
            .resourceRequirements(resourceRequirements);

        assertEquals(expectedConnectionRead, actualConnectionRead);
        verify(configRepository).writeStandardSync(expectedPersistedSync);
        verify(eventRunner).update(connectionUpdate.getConnectionId());
      }

      @Test
      void testValidateConnectionUpdateOperationInDifferentWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
        when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(UUID.randomUUID());
        when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

        final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
            .connectionId(standardSync.getConnectionId())
            .operationIds(Collections.singletonList(operationId))
            .syncCatalog(CatalogConverter.toApi(standardSync.getCatalog(), standardSync.getFieldSelectionData()));

        assertThrows(IllegalArgumentException.class, () -> connectionsHandler.updateConnection(connectionUpdate));
      }

    }

    @Test
    void testGetConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);

      final ConnectionRead actualConnectionRead = connectionsHandler.getConnection(standardSync.getConnectionId());

      assertEquals(ConnectionHelpers.generateExpectedConnectionRead(standardSync), actualConnectionRead);
    }

    @Test
    void testListConnectionsForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(configRepository.listWorkspaceStandardSyncs(source.getWorkspaceId(), false))
          .thenReturn(Lists.newArrayList(standardSync));
      when(configRepository.listWorkspaceStandardSyncs(source.getWorkspaceId(), true))
          .thenReturn(Lists.newArrayList(standardSync, standardSyncDeleted));
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);

      final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(source.getWorkspaceId());
      final ConnectionReadList actualConnectionReadList = connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(
          ConnectionHelpers.generateExpectedConnectionRead(standardSync),
          actualConnectionReadList.getConnections().get(0));

      final ConnectionReadList actualConnectionReadListWithDeleted = connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody, true);
      final List<ConnectionRead> connections = actualConnectionReadListWithDeleted.getConnections();
      assertEquals(2, connections.size());
      assertEquals(ApiPojoConverters.internalToConnectionRead(standardSync), connections.get(0));
      assertEquals(ApiPojoConverters.internalToConnectionRead(standardSyncDeleted), connections.get(1));

    }

    @Test
    void testListConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(configRepository.listStandardSyncs())
          .thenReturn(Lists.newArrayList(standardSync));
      when(configRepository.getSourceConnection(source.getSourceId()))
          .thenReturn(source);
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);

      final ConnectionReadList actualConnectionReadList = connectionsHandler.listConnections();

      assertEquals(
          ConnectionHelpers.generateExpectedConnectionRead(standardSync),
          actualConnectionReadList.getConnections().get(0));
    }

    @Test
    void testSearchConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
      final ConnectionRead connectionRead1 = ConnectionHelpers.connectionReadFromStandardSync(standardSync);
      final StandardSync standardSync2 = new StandardSync()
          .withConnectionId(UUID.randomUUID())
          .withName("test connection")
          .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.CUSTOMFORMAT)
          .withNamespaceFormat("ns_format")
          .withPrefix("test_prefix")
          .withStatus(StandardSync.Status.ACTIVE)
          .withCatalog(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog())
          .withSourceId(sourceId)
          .withDestinationId(destinationId)
          .withOperationIds(List.of(operationId))
          .withManual(true)
          .withResourceRequirements(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS)
          .withGeography(Geography.US)
          .withBreakingChange(false);
      final ConnectionRead connectionRead2 = ConnectionHelpers.connectionReadFromStandardSync(standardSync2);
      final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
          .withName(SOURCE_TEST)
          .withSourceDefinitionId(UUID.randomUUID());
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withName(DESTINATION_TEST)
          .withDestinationDefinitionId(UUID.randomUUID());

      when(configRepository.listStandardSyncs())
          .thenReturn(Lists.newArrayList(standardSync, standardSync2));
      when(configRepository.getSourceConnection(source.getSourceId()))
          .thenReturn(source);
      when(configRepository.getDestinationConnection(destination.getDestinationId()))
          .thenReturn(destination);
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);
      when(configRepository.getStandardSync(standardSync2.getConnectionId()))
          .thenReturn(standardSync2);
      when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
          .thenReturn(sourceDefinition);
      when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
          .thenReturn(destinationDefinition);

      final ConnectionSearch connectionSearch = new ConnectionSearch();
      connectionSearch.namespaceDefinition(NamespaceDefinitionType.SOURCE);
      ConnectionReadList actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(null);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      final SourceSearch sourceSearch = new SourceSearch().sourceId(UUID.randomUUID());
      connectionSearch.setSource(sourceSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      sourceSearch.sourceId(connectionRead1.getSourceId());
      connectionSearch.setSource(sourceSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      final DestinationSearch destinationSearch = new DestinationSearch();
      connectionSearch.setDestination(destinationSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      destinationSearch.connectionConfiguration(Jsons.jsonNode(Collections.singletonMap("apiKey", "not-found")));
      connectionSearch.setDestination(destinationSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      destinationSearch.connectionConfiguration(Jsons.jsonNode(Collections.singletonMap("apiKey", "123-abc")));
      connectionSearch.setDestination(destinationSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      connectionSearch.name("non-existent");
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      connectionSearch.name(connectionRead1.getName());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.name(connectionRead2.getName());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(connectionRead1.getNamespaceDefinition());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      connectionSearch.name(null);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(connectionRead2.getNamespaceDefinition());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(null);
      connectionSearch.status(ConnectionStatus.INACTIVE);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      connectionSearch.status(ConnectionStatus.ACTIVE);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      connectionSearch.prefix(connectionRead1.getPrefix());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.prefix(connectionRead2.getPrefix());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(0));
    }

    @Test
    void testDeleteConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
      connectionsHandler.deleteConnection(connectionId);

      verify(connectionHelper).deleteConnection(connectionId);
    }

    @Test
    void failOnUnmatchedWorkspacesInCreate() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(standardSync.getSourceId())).thenReturn(UUID.randomUUID());
      when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(standardSync.getDestinationId())).thenReturn(UUID.randomUUID());
      when(configRepository.getSourceConnection(source.getSourceId()))
          .thenReturn(source);
      when(configRepository.getDestinationConnection(destination.getDestinationId()))
          .thenReturn(destination);

      when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
      final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
          .withName(SOURCE_TEST)
          .withSourceDefinitionId(UUID.randomUUID());
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withName(DESTINATION_TEST)
          .withDestinationDefinitionId(UUID.randomUUID());
      when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
      when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(sourceDefinition);
      when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(destinationDefinition);

      final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

      final ConnectionCreate connectionCreate = new ConnectionCreate()
          .sourceId(standardSync.getSourceId())
          .destinationId(standardSync.getDestinationId())
          .operationIds(standardSync.getOperationIds())
          .name(PRESTO_TO_HUDI)
          .namespaceDefinition(NamespaceDefinitionType.SOURCE)
          .namespaceFormat(null)
          .prefix(PRESTO_TO_HUDI_PREFIX)
          .status(ConnectionStatus.ACTIVE)
          .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
          .syncCatalog(catalog)
          .resourceRequirements(new io.airbyte.api.model.generated.ResourceRequirements()
              .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
              .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
              .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest())
              .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit()));

      Assert.assertThrows(IllegalArgumentException.class, () -> {
        connectionsHandler.createConnection(connectionCreate);
      });
    }

    @Test
    void testEnumConversion() {
      assertTrue(Enums.isCompatible(ConnectionStatus.class, StandardSync.Status.class));
      assertTrue(Enums.isCompatible(io.airbyte.config.SyncMode.class, SyncMode.class));
      assertTrue(Enums.isCompatible(StandardSync.Status.class, ConnectionStatus.class));
      assertTrue(Enums.isCompatible(ConnectionSchedule.TimeUnitEnum.class, Schedule.TimeUnit.class));
      assertTrue(Enums.isCompatible(io.airbyte.api.model.generated.DataType.class, DataType.class));
      assertTrue(Enums.isCompatible(DataType.class, io.airbyte.api.model.generated.DataType.class));
      assertTrue(Enums.isCompatible(NamespaceDefinitionType.class, io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.class));
    }

  }

  @Nested
  class StreamConfigurationDiff {

    @BeforeEach
    void setUp() {
      connectionsHandler = new ConnectionsHandler(
          configRepository,
          uuidGenerator,
          workspaceHelper,
          trackingClient,
          eventRunner,
          connectionHelper);
    }

    @Test
    void testNoDiff() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));

      assertTrue(connectionsHandler.getConfigurationDiff(catalog1, catalog2).isEmpty());
    }

    @Test
    void testNoDiffIfStreamAdded() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));

      assertTrue(connectionsHandler.getConfigurationDiff(catalog1, catalog2).isEmpty());
    }

    @Test
    void testCursorOrderDoesMatter() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1, "anotherCursor"),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration1WithOtherCursorOrder = getStreamConfiguration(
          List.of("anotherCursor", CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1WithOtherCursorOrder),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));

      final Set<StreamDescriptor> changedSd = connectionsHandler.getConfigurationDiff(catalog1, catalog2);
      assertFalse(changedSd.isEmpty());
      assertEquals(1, changedSd.size());
      assertEquals(Set.of(new StreamDescriptor().name(STREAM1)), changedSd);
    }

    @Test
    void testPkOrderDoesntMatter() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1, PK3)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration1WithOtherPkOrder = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK3, PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2), List.of(PK3)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteStreamConfiguration streamConfiguration2WithOtherPkOrder = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK3), List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1WithOtherPkOrder),
                  getStreamAndConfig(STREAM2, streamConfiguration2WithOtherPkOrder)));

      final Set<StreamDescriptor> changedSd = connectionsHandler.getConfigurationDiff(catalog1, catalog2);
      assertFalse(changedSd.isEmpty());
      assertEquals(1, changedSd.size());
      assertEquals(Set.of(new StreamDescriptor().name(STREAM1)), changedSd);
    }

    @Test
    void testNoDiffIfStreamRemove() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1)));

      assertTrue(connectionsHandler.getConfigurationDiff(catalog1, catalog2).isEmpty());
    }

    @Test
    void testDiffDifferentCursor() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration1CursorDiff = getStreamConfiguration(
          List.of(CURSOR1, "anotherCursor"),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1CursorDiff),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));

      final Set<StreamDescriptor> changedSd = connectionsHandler.getConfigurationDiff(catalog1, catalog2);
      assertFalse(changedSd.isEmpty());
      assertEquals(1, changedSd.size());
      assertEquals(Set.of(new StreamDescriptor().name(STREAM1)), changedSd);
    }

    @Test
    void testDiffIfDifferentPrimaryKey() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration1WithPkDiff = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1, PK3)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2WithPkDiff = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1), List.of(PK3)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1WithPkDiff),
                  getStreamAndConfig(STREAM2, streamConfiguration2WithPkDiff)));

      final Set<StreamDescriptor> changedSd = connectionsHandler.getConfigurationDiff(catalog1, catalog2);
      assertFalse(changedSd.isEmpty());
      assertEquals(2, changedSd.size());
      Assertions.assertThat(changedSd)
          .containsExactlyInAnyOrder(new StreamDescriptor().name(STREAM1), new StreamDescriptor().name(STREAM2));
    }

    @Test
    void testDiffDifferentSyncMode() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration1CursorDiff = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1CursorDiff),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));

      final Set<StreamDescriptor> changedSd = connectionsHandler.getConfigurationDiff(catalog1, catalog2);
      assertFalse(changedSd.isEmpty());
      assertEquals(1, changedSd.size());
      assertEquals(Set.of(new StreamDescriptor().name(STREAM1)), changedSd);
    }

    @Test
    void testDiffDifferentDestinationSyncMode() {
      final AirbyteStreamConfiguration streamConfiguration1 = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND_DEDUP);

      final AirbyteStreamConfiguration streamConfiguration1CursorDiff = getStreamConfiguration(
          List.of(CURSOR1),
          List.of(List.of(PK1)),
          SyncMode.INCREMENTAL,
          DestinationSyncMode.APPEND);

      final AirbyteStreamConfiguration streamConfiguration2 = getStreamConfiguration(
          List.of(CURSOR2),
          List.of(List.of(PK2)),
          SyncMode.FULL_REFRESH,
          DestinationSyncMode.OVERWRITE);

      final AirbyteCatalog catalog1 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));
      final AirbyteCatalog catalog2 = new AirbyteCatalog()
          .streams(
              List.of(
                  getStreamAndConfig(STREAM1, streamConfiguration1CursorDiff),
                  getStreamAndConfig(STREAM2, streamConfiguration2)));

      final Set<StreamDescriptor> changedSd = connectionsHandler.getConfigurationDiff(catalog1, catalog2);
      assertFalse(changedSd.isEmpty());
      assertEquals(1, changedSd.size());
      assertEquals(Set.of(new StreamDescriptor().name(STREAM1)), changedSd);
    }

    private AirbyteStreamAndConfiguration getStreamAndConfig(final String name, final AirbyteStreamConfiguration config) {
      return new AirbyteStreamAndConfiguration()
          .config(config)
          .stream(new AirbyteStream().name(name));
    }

    private AirbyteStreamConfiguration getStreamConfiguration(final List<String> cursors,
                                                              final List<List<String>> primaryKeys,
                                                              final SyncMode syncMode,
                                                              final DestinationSyncMode destinationSyncMode) {
      return new AirbyteStreamConfiguration()
          .cursorField(cursors)
          .primaryKey(primaryKeys)
          .syncMode(syncMode)
          .destinationSyncMode(destinationSyncMode);

    }

  }

}
