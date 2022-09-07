/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.jooq.JSONB;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class StatePersistenceTest extends BaseDatabaseConfigPersistenceTest {

  private ConfigRepository configRepository;
  private StatePersistence statePersistence;
  private UUID connectionId;
  private static final String STATE_ONE = "\"state1\"";
  private static final String STATE_TWO = "\"state2\"";
  private static final String STATE_WITH_NAMESPACE = "\"state s1.n1\"";
  private static final String STREAM_STATE_2 = "\"state s2\"";
  private static final String GLOBAL_STATE = "\"my global state\"";
  private static final String STATE = "state";

  @Test
  void testReadingNonExistingState() throws IOException {
    Assertions.assertTrue(statePersistence.getCurrentState(UUID.randomUUID()).isEmpty());
  }

  @Test
  void testLegacyReadWrite() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.LEGACY)
        .withLegacyState(Jsons.deserialize("{\"woot\": \"legacy states is passthrough\"}"));

    // Initial write/read loop, making sure we read what we wrote
    statePersistence.updateOrCreateState(connectionId, state0);
    final Optional<StateWrapper> state1 = statePersistence.getCurrentState(connectionId);

    Assertions.assertTrue(state1.isPresent());
    Assertions.assertEquals(StateType.LEGACY, state1.get().getStateType());
    Assertions.assertEquals(state0.getLegacyState(), state1.get().getLegacyState());

    // Updating a state
    final JsonNode newStateJson = Jsons.deserialize("{\"woot\": \"new state\"}");
    final StateWrapper state2 = clone(state1.get()).withLegacyState(newStateJson);
    statePersistence.updateOrCreateState(connectionId, state2);
    final Optional<StateWrapper> state3 = statePersistence.getCurrentState(connectionId);

    Assertions.assertTrue(state3.isPresent());
    Assertions.assertEquals(StateType.LEGACY, state3.get().getStateType());
    Assertions.assertEquals(newStateJson, state3.get().getLegacyState());

    // Deleting a state
    final StateWrapper state4 = clone(state3.get()).withLegacyState(null);
    statePersistence.updateOrCreateState(connectionId, state4);
    Assertions.assertTrue(statePersistence.getCurrentState(connectionId).isEmpty());
  }

  @Test
  void testLegacyMigrationToGlobal() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.LEGACY)
        .withLegacyState(Jsons.deserialize("{\"woot\": \"legacy states is passthrough\"}"));

    statePersistence.updateOrCreateState(connectionId, state0);

    final StateWrapper newGlobalState = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(Jsons.deserialize("\"woot\""))
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n2"))
                        .withStreamState(Jsons.deserialize(STATE_ONE)),
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1"))
                        .withStreamState(Jsons.deserialize(STATE_TWO))))));
    statePersistence.updateOrCreateState(connectionId, newGlobalState);
    final StateWrapper storedGlobalState = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(newGlobalState, storedGlobalState);
  }

  @Test
  void testLegacyMigrationToStream() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.LEGACY)
        .withLegacyState(Jsons.deserialize("{\"woot\": \"legacy states is passthrough\"}"));

    statePersistence.updateOrCreateState(connectionId, state0);

    final StateWrapper newStreamState = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Arrays.asList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                    .withStreamState(Jsons.deserialize(STATE_WITH_NAMESPACE))),
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                    .withStreamState(Jsons.deserialize(STREAM_STATE_2)))));
    statePersistence.updateOrCreateState(connectionId, newStreamState);
    final StateWrapper storedStreamState = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(newStreamState, storedStreamState);
  }

  @Test
  void testGlobalReadWrite() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(Jsons.deserialize(GLOBAL_STATE))
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n2"))
                        .withStreamState(Jsons.deserialize(STATE_ONE)),
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1"))
                        .withStreamState(Jsons.deserialize(STATE_TWO))))));

    // Initial write/read loop, making sure we read what we wrote
    statePersistence.updateOrCreateState(connectionId, state0);
    final Optional<StateWrapper> state1 = statePersistence.getCurrentState(connectionId);
    Assertions.assertTrue(state1.isPresent());
    assertEquals(state0, state1.get());

    // Updating a state
    final StateWrapper state2 = clone(state1.get());
    state2.getGlobal()
        .getGlobal().withSharedState(Jsons.deserialize("\"updated shared state\""))
        .getStreamStates().get(1).withStreamState(Jsons.deserialize("\"updated state2\""));
    statePersistence.updateOrCreateState(connectionId, state2);
    final Optional<StateWrapper> state3 = statePersistence.getCurrentState(connectionId);

    Assertions.assertTrue(state3.isPresent());
    assertEquals(state2, state3.get());

    // Updating a state with name and namespace
    final StateWrapper state4 = clone(state1.get());
    state4.getGlobal().getGlobal()
        .getStreamStates().get(0).withStreamState(Jsons.deserialize("\"updated state1\""));
    statePersistence.updateOrCreateState(connectionId, state4);
    final Optional<StateWrapper> state5 = statePersistence.getCurrentState(connectionId);

    Assertions.assertTrue(state5.isPresent());
    assertEquals(state4, state5.get());
  }

  @Test
  void testGlobalPartialReset() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(Jsons.deserialize(GLOBAL_STATE))
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n2"))
                        .withStreamState(Jsons.deserialize(STATE_ONE)),
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1"))
                        .withStreamState(Jsons.deserialize(STATE_TWO))))));

    // Set the initial state
    statePersistence.updateOrCreateState(connectionId, state0);

    // incomplete reset does not remove the state
    final StateWrapper incompletePartialReset = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(Jsons.deserialize(GLOBAL_STATE))
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1"))
                        .withStreamState(Jsons.deserialize(STATE_TWO))))));
    statePersistence.updateOrCreateState(connectionId, incompletePartialReset);
    final StateWrapper incompletePartialResetResult = statePersistence.getCurrentState(connectionId).orElseThrow();
    Assertions.assertEquals(state0, incompletePartialResetResult);

    // The good partial reset
    final StateWrapper partialReset = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(Jsons.deserialize(GLOBAL_STATE))
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n2"))
                        .withStreamState(Jsons.deserialize(STATE_ONE)),
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1"))
                        .withStreamState(null)))));
    statePersistence.updateOrCreateState(connectionId, partialReset);
    final StateWrapper partialResetResult = statePersistence.getCurrentState(connectionId).orElseThrow();

    Assertions.assertEquals(partialReset.getGlobal().getGlobal().getSharedState(),
        partialResetResult.getGlobal().getGlobal().getSharedState());
    // {"name": "s1"} should have been removed from the stream states
    Assertions.assertEquals(1, partialResetResult.getGlobal().getGlobal().getStreamStates().size());
    Assertions.assertEquals(partialReset.getGlobal().getGlobal().getStreamStates().get(0),
        partialResetResult.getGlobal().getGlobal().getStreamStates().get(0));
  }

  @Test
  void testGlobalFullReset() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(Jsons.deserialize(GLOBAL_STATE))
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n2"))
                        .withStreamState(Jsons.deserialize(STATE_ONE)),
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1"))
                        .withStreamState(Jsons.deserialize(STATE_TWO))))));

    final StateWrapper fullReset = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(null)
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n2"))
                        .withStreamState(null),
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1"))
                        .withStreamState(null)))));;

    statePersistence.updateOrCreateState(connectionId, state0);
    statePersistence.updateOrCreateState(connectionId, fullReset);
    final Optional<StateWrapper> fullResetResult = statePersistence.getCurrentState(connectionId);
    Assertions.assertTrue(fullResetResult.isEmpty());
  }

  @Test
  void testGlobalStateAllowsEmptyNameAndNamespace() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(Jsons.deserialize(GLOBAL_STATE))
                .withStreamStates(Arrays.asList(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName(""))
                        .withStreamState(Jsons.deserialize("\"empty name state\"")),
                    new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("").withNamespace(""))
                        .withStreamState(Jsons.deserialize("\"empty name and namespace state\""))))));

    statePersistence.updateOrCreateState(connectionId, state0);
    final StateWrapper state1 = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(state0, state1);
  }

  @Test
  void testStreamReadWrite() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Arrays.asList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                    .withStreamState(Jsons.deserialize(STATE_WITH_NAMESPACE))),
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                    .withStreamState(Jsons.deserialize(STREAM_STATE_2)))));

    // Initial write/read loop, making sure we read what we wrote
    statePersistence.updateOrCreateState(connectionId, state0);
    final StateWrapper state1 = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(state0, state1);

    // Updating a state
    final StateWrapper state2 = clone(state1);
    state2.getStateMessages().get(1).getStream().withStreamState(Jsons.deserialize("\"updated state s2\""));
    statePersistence.updateOrCreateState(connectionId, state2);
    final StateWrapper state3 = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(state2, state3);

    // Updating a state with name and namespace
    final StateWrapper state4 = clone(state1);
    state4.getStateMessages().get(0).getStream().withStreamState(Jsons.deserialize("\"updated state s1\""));
    statePersistence.updateOrCreateState(connectionId, state4);
    final StateWrapper state5 = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(state4, state5);
  }

  @Test
  void testStreamPartialUpdates() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Arrays.asList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                    .withStreamState(Jsons.deserialize(STATE_WITH_NAMESPACE))),
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                    .withStreamState(Jsons.deserialize(STREAM_STATE_2)))));

    statePersistence.updateOrCreateState(connectionId, state0);

    // Partial update
    final StateWrapper partialUpdate = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Collections.singletonList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                    .withStreamState(Jsons.deserialize("\"updated\"")))));
    statePersistence.updateOrCreateState(connectionId, partialUpdate);
    final StateWrapper partialUpdateResult = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(
        new StateWrapper()
            .withStateType(StateType.STREAM)
            .withStateMessages(Arrays.asList(
                new AirbyteStateMessage()
                    .withType(AirbyteStateType.STREAM)
                    .withStream(new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                        .withStreamState(Jsons.deserialize("\"updated\""))),
                new AirbyteStateMessage()
                    .withType(AirbyteStateType.STREAM)
                    .withStream(new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                        .withStreamState(Jsons.deserialize(STREAM_STATE_2))))),
        partialUpdateResult);

    // Partial Reset
    final StateWrapper partialReset = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Collections.singletonList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                    .withStreamState(null))));
    statePersistence.updateOrCreateState(connectionId, partialReset);
    final StateWrapper partialResetResult = statePersistence.getCurrentState(connectionId).orElseThrow();
    assertEquals(
        new StateWrapper()
            .withStateType(StateType.STREAM)
            .withStateMessages(Arrays.asList(
                new AirbyteStateMessage()
                    .withType(AirbyteStateType.STREAM)
                    .withStream(new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                        .withStreamState(Jsons.deserialize("\"updated\""))))),
        partialResetResult);
  }

  @Test
  void testStreamFullReset() throws IOException {
    final StateWrapper state0 = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Arrays.asList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                    .withStreamState(Jsons.deserialize(STATE_WITH_NAMESPACE))),
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                    .withStreamState(Jsons.deserialize(STREAM_STATE_2)))));

    statePersistence.updateOrCreateState(connectionId, state0);

    // Partial update
    final StateWrapper fullReset = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Arrays.asList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                    .withStreamState(null)),
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                    .withStreamState(null))));
    statePersistence.updateOrCreateState(connectionId, fullReset);
    final Optional<StateWrapper> fullResetResult = statePersistence.getCurrentState(connectionId);
    Assertions.assertTrue(fullResetResult.isEmpty());
  }

  @Test
  void testInconsistentTypeUpdates() throws IOException {
    final StateWrapper streamState = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Arrays.asList(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s1").withNamespace("n1"))
                    .withStreamState(Jsons.deserialize(STATE_WITH_NAMESPACE))),
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withName("s2"))
                    .withStreamState(Jsons.deserialize(STREAM_STATE_2)))));
    statePersistence.updateOrCreateState(connectionId, streamState);

    Assertions.assertThrows(IllegalStateException.class, () -> {
      final StateWrapper globalState = new StateWrapper()
          .withStateType(StateType.GLOBAL)
          .withGlobal(new AirbyteStateMessage()
              .withType(AirbyteStateType.GLOBAL)
              .withGlobal(new AirbyteGlobalState()
                  .withSharedState(Jsons.deserialize(GLOBAL_STATE))
                  .withStreamStates(Arrays.asList(
                      new AirbyteStreamState()
                          .withStreamDescriptor(new StreamDescriptor().withName(""))
                          .withStreamState(Jsons.deserialize("\"empty name state\"")),
                      new AirbyteStreamState()
                          .withStreamDescriptor(new StreamDescriptor().withName("").withNamespace(""))
                          .withStreamState(Jsons.deserialize("\"empty name and namespace state\""))))));
      statePersistence.updateOrCreateState(connectionId, globalState);
    });

    // We should be guarded against those cases let's make sure we don't make things worse if we're in
    // an inconsistent state
    dslContext.insertInto(DSL.table(STATE))
        .columns(DSL.field("id"), DSL.field("connection_id"), DSL.field("type"), DSL.field(STATE))
        .values(UUID.randomUUID(), connectionId, io.airbyte.db.instance.configs.jooq.generated.enums.StateType.GLOBAL, JSONB.valueOf("{}"))
        .execute();
    Assertions.assertThrows(IllegalStateException.class, () -> statePersistence.updateOrCreateState(connectionId, streamState));
    Assertions.assertThrows(IllegalStateException.class, () -> statePersistence.getCurrentState(connectionId));
  }

  @Test
  void testEnumsConversion() {
    // Making sure StateType we write to the DB and the StateType from the protocols are aligned.
    // Otherwise, we'll have to dig through runtime errors.
    Assertions.assertTrue(Enums.isCompatible(
        io.airbyte.db.instance.configs.jooq.generated.enums.StateType.class,
        io.airbyte.config.StateType.class));
  }

  @Test
  void testStatePersistenceLegacyReadConsistency() throws IOException {
    final JsonNode jsonState = Jsons.deserialize("{\"my\": \"state\"}");
    final State state = new State().withState(jsonState);
    configRepository.updateConnectionState(connectionId, state);

    final StateWrapper readStateWrapper = statePersistence.getCurrentState(connectionId).orElseThrow();
    Assertions.assertEquals(StateType.LEGACY, readStateWrapper.getStateType());
    Assertions.assertEquals(state.getState(), readStateWrapper.getLegacyState());
  }

  @Test
  void testStatePersistenceLegacyWriteConsistency() throws IOException {
    final JsonNode jsonState = Jsons.deserialize("{\"my\": \"state\"}");
    final StateWrapper stateWrapper = new StateWrapper().withStateType(StateType.LEGACY).withLegacyState(jsonState);
    statePersistence.updateOrCreateState(connectionId, stateWrapper);

    // Making sure we still follow the legacy format
    final List<State> readStates = dslContext
        .selectFrom(STATE)
        .where(DSL.field("connection_id").eq(connectionId))
        .fetch().map(r -> Jsons.deserialize(r.get(DSL.field(STATE, JSONB.class)).data(), State.class))
        .stream().toList();
    Assertions.assertEquals(1, readStates.size());

    Assertions.assertEquals(readStates.get(0).getState(), stateWrapper.getLegacyState());
  }

  @BeforeEach
  void beforeEach() throws DatabaseInitializationException, IOException, JsonValidationException {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    flyway = FlywayFactory.create(dataSource, DatabaseConfigPersistenceLoadDataTest.class.getName(),
        ConfigsDatabaseMigrator.DB_IDENTIFIER, ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    database = new ConfigsDatabaseTestProvider(dslContext, flyway).create(true);
    setupTestData();

    statePersistence = new StatePersistence(database);
  }

  @AfterEach
  void afterEach() {
    // Making sure we reset between tests
    dslContext.dropSchemaIfExists("public").cascade().execute();
    dslContext.createSchema("public").execute();
    dslContext.setSchema("public").execute();
  }

  private void setupTestData() throws JsonValidationException, IOException {
    configRepository = new ConfigRepository(
        new DatabaseConfigPersistence(database, mock(JsonSecretsProcessor.class)),
        database);

    final StandardWorkspace workspace = MockData.standardWorkspaces().get(0);
    final StandardSourceDefinition sourceDefinition = MockData.publicSourceDefinition();
    final SourceConnection sourceConnection = MockData.sourceConnections().get(0);
    final StandardDestinationDefinition destinationDefinition = MockData.publicDestinationDefinition();
    final DestinationConnection destinationConnection = MockData.destinationConnections().get(0);
    final StandardSync sync = MockData.standardSyncs().get(0);

    configRepository.writeStandardWorkspace(workspace);
    configRepository.writeStandardSourceDefinition(sourceDefinition);
    configRepository.writeSourceConnectionNoSecrets(sourceConnection);
    configRepository.writeStandardDestinationDefinition(destinationDefinition);
    configRepository.writeDestinationConnectionNoSecrets(destinationConnection);
    configRepository.writeStandardSyncOperation(MockData.standardSyncOperations().get(0));
    configRepository.writeStandardSyncOperation(MockData.standardSyncOperations().get(1));
    configRepository.writeStandardSync(sync);

    connectionId = sync.getConnectionId();
  }

  private StateWrapper clone(final StateWrapper state) {
    return switch (state.getStateType()) {
      case LEGACY -> new StateWrapper()
          .withLegacyState(Jsons.deserialize(Jsons.serialize(state.getLegacyState())))
          .withStateType(state.getStateType());
      case STREAM -> new StateWrapper()
          .withStateMessages(
              state.getStateMessages().stream().map(msg -> Jsons.deserialize(Jsons.serialize(msg), AirbyteStateMessage.class)).toList())
          .withStateType(state.getStateType());
      case GLOBAL -> new StateWrapper()
          .withGlobal(Jsons.deserialize(Jsons.serialize(state.getGlobal()), AirbyteStateMessage.class))
          .withStateType(state.getStateType());
    };
  }

  private void assertEquals(final StateWrapper lhs, final StateWrapper rhs) {
    Assertions.assertEquals(Jsons.serialize(lhs), Jsons.serialize(rhs));
  }

}
