/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.State;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class EmptyAirbyteSourceTest {

  private EmptyAirbyteSource emptyAirbyteSource;
  private final AirbyteMessage EMPTY_MESSAGE =
      new AirbyteMessage().withType(Type.STATE)
          .withState(new AirbyteStateMessage().withStateType(AirbyteStateType.LEGACY).withData(Jsons.emptyObject()));

  @BeforeEach
  public void init() {
    emptyAirbyteSource = new EmptyAirbyteSource();
  }

  @Test
  public void testLegacy() throws Exception {
    emptyAirbyteSource.start(new WorkerSourceConfig(), null);

    legacyStateResult();
  }

  @Test
  public void testEmptyListOfStreams() throws Exception {
    ResetSourceConfiguration resetSourceConfiguration = new ResetSourceConfiguration()
        .withStreamsToReset(new ArrayList<>());
    WorkerSourceConfig workerSourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(Jsons.jsonNode(resetSourceConfiguration));

    emptyAirbyteSource.start(workerSourceConfig, null);

    legacyStateResult();
  }

  @Test
  public void nonStartedSource() {
    Throwable thrown = Assertions.catchThrowable(() -> emptyAirbyteSource.attemptRead());
    Assertions.assertThat(thrown)
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  public void testGlobal() throws Exception {
    List<StreamDescriptor> streamDescriptors = Lists.newArrayList(
        new StreamDescriptor().withName("a"),
        new StreamDescriptor().withName("b"),
        new StreamDescriptor().withName("c"));

    List<io.airbyte.config.StreamDescriptor> streamToReset = Lists.newArrayList(
        new io.airbyte.config.StreamDescriptor().withName("a"),
        new io.airbyte.config.StreamDescriptor().withName("b"),
        new io.airbyte.config.StreamDescriptor().withName("c"));

    ResetSourceConfiguration resetSourceConfiguration = new ResetSourceConfiguration()
        .withStreamsToReset(streamToReset);
    WorkerSourceConfig workerSourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(Jsons.jsonNode(resetSourceConfiguration))
        .withState(new State()
            .withState(Jsons.jsonNode(createGlobalState(streamDescriptors, Jsons.emptyObject()))));

    emptyAirbyteSource.start(workerSourceConfig, null);

    Optional<AirbyteMessage> maybeMessage = emptyAirbyteSource.attemptRead();
    Assertions.assertThat(maybeMessage)
        .isNotEmpty();

    AirbyteMessage message = maybeMessage.get();
    Assertions.assertThat(message.getType()).isEqualTo(Type.STATE);

    /*
     * The comparison could be what it is bellow but it makes it hard to see what is the diff. It has
     * been break dow into multiples assertions. (same comment in the other tests)
     *
     * AirbyteStateMessage expectedState = new AirbyteStateMessage()
     * .withStateType(AirbyteStateType.GLOBAL) .withGlobal( new AirbyteGlobalState()
     * .withSharedState(Jsons.emptyObject()) .withStreamStates( Lists.newArrayList( new
     * AirbyteStreamState().withStreamState(null).withStreamDescriptor(new
     * StreamDescriptor().withName("a")), new
     * AirbyteStreamState().withStreamState(null).withStreamDescriptor(new
     * StreamDescriptor().withName("b")), new
     * AirbyteStreamState().withStreamState(Jsons.emptyObject()).withStreamDescriptor(new
     * StreamDescriptor().withName("c")) ) ) );
     *
     * Assertions.assertThat(stateMessage).isEqualTo(expectedState);
     */
    AirbyteStateMessage stateMessage = message.getState();
    Assertions.assertThat(stateMessage.getStateType()).isEqualTo(AirbyteStateType.GLOBAL);
    Assertions.assertThat(stateMessage.getGlobal().getSharedState()).isNull();
    Assertions.assertThat(stateMessage.getGlobal().getStreamStates())
        .map(streamState -> streamState.getStreamDescriptor())
        .containsExactlyElementsOf(streamDescriptors);
    Assertions.assertThat(stateMessage.getGlobal().getStreamStates())
        .map(streamState -> streamState.getStreamState())
        .containsOnlyNulls();

    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isEmpty();
  }

  @Test
  public void testGlobalPartial() throws Exception {
    final String NOT_RESET_STREAM_NAME = "c";

    List<StreamDescriptor> streamDescriptors = Lists.newArrayList(
        new StreamDescriptor().withName("a"),
        new StreamDescriptor().withName("b"),
        new StreamDescriptor().withName(NOT_RESET_STREAM_NAME));

    List<io.airbyte.config.StreamDescriptor> streamToReset = Lists.newArrayList(
        new io.airbyte.config.StreamDescriptor().withName("a"),
        new io.airbyte.config.StreamDescriptor().withName("b"));

    ResetSourceConfiguration resetSourceConfiguration = new ResetSourceConfiguration()
        .withStreamsToReset(streamToReset);
    WorkerSourceConfig workerSourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(Jsons.jsonNode(resetSourceConfiguration))
        .withState(new State()
            .withState(Jsons.jsonNode(createGlobalState(streamDescriptors, Jsons.emptyObject()))));

    emptyAirbyteSource.start(workerSourceConfig, null);

    Optional<AirbyteMessage> maybeMessage = emptyAirbyteSource.attemptRead();
    Assertions.assertThat(maybeMessage)
        .isNotEmpty();

    AirbyteMessage message = maybeMessage.get();
    Assertions.assertThat(message.getType()).isEqualTo(Type.STATE);

    AirbyteStateMessage stateMessage = message.getState();

    Assertions.assertThat(stateMessage.getStateType()).isEqualTo(AirbyteStateType.GLOBAL);
    Assertions.assertThat(stateMessage.getGlobal().getSharedState()).isEqualTo(Jsons.emptyObject());
    Assertions.assertThat(stateMessage.getGlobal().getStreamStates())
        .filteredOn(streamState -> streamState.getStreamDescriptor().getName() != NOT_RESET_STREAM_NAME)
        .map(AirbyteStreamState::getStreamState)
        .containsOnlyNulls();
    Assertions.assertThat(stateMessage.getGlobal().getStreamStates())
        .filteredOn(streamState -> streamState.getStreamDescriptor().getName() == NOT_RESET_STREAM_NAME)
        .map(AirbyteStreamState::getStreamState)
        .contains(Jsons.emptyObject());

    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isEmpty();
  }

  @Test
  public void testGlobalNewStream() throws Exception {
    final String NEW_STREAM = "c";

    List<StreamDescriptor> streamDescriptors = Lists.newArrayList(
        new StreamDescriptor().withName("a"),
        new StreamDescriptor().withName("b"));

    List<io.airbyte.config.StreamDescriptor> streamToReset = Lists.newArrayList(
        new io.airbyte.config.StreamDescriptor().withName("a"),
        new io.airbyte.config.StreamDescriptor().withName("b"),
        new io.airbyte.config.StreamDescriptor().withName(NEW_STREAM));

    ResetSourceConfiguration resetSourceConfiguration = new ResetSourceConfiguration()
        .withStreamsToReset(streamToReset);
    WorkerSourceConfig workerSourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(Jsons.jsonNode(resetSourceConfiguration))
        .withState(new State()
            .withState(Jsons.jsonNode(createGlobalState(streamDescriptors, Jsons.emptyObject()))));

    emptyAirbyteSource.start(workerSourceConfig, null);

    Optional<AirbyteMessage> maybeMessage = emptyAirbyteSource.attemptRead();
    Assertions.assertThat(maybeMessage)
        .isNotEmpty();

    AirbyteMessage message = maybeMessage.get();
    Assertions.assertThat(message.getType()).isEqualTo(Type.STATE);

    AirbyteStateMessage stateMessage = message.getState();

    Assertions.assertThat(stateMessage.getStateType()).isEqualTo(AirbyteStateType.GLOBAL);
    Assertions.assertThat(stateMessage.getGlobal().getSharedState()).isNull();
    Assertions.assertThat(stateMessage.getGlobal().getStreamStates())
        .map(AirbyteStreamState::getStreamState)
        .containsOnlyNulls();
    Assertions.assertThat(stateMessage.getGlobal().getStreamStates())
        .filteredOn(streamState -> streamState.getStreamDescriptor().getName() == NEW_STREAM)
        .hasSize(1);

    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isEmpty();
  }

  @Test
  public void testPerStream() throws Exception {
    List<StreamDescriptor> streamDescriptors = Lists.newArrayList(
        new StreamDescriptor().withName("a"),
        new StreamDescriptor().withName("b"),
        new StreamDescriptor().withName("c"));

    List<io.airbyte.config.StreamDescriptor> streamToReset = Lists.newArrayList(
        new io.airbyte.config.StreamDescriptor().withName("a"),
        new io.airbyte.config.StreamDescriptor().withName("b"),
        new io.airbyte.config.StreamDescriptor().withName("c"));

    ResetSourceConfiguration resetSourceConfiguration = new ResetSourceConfiguration()
        .withStreamsToReset(streamToReset);
    WorkerSourceConfig workerSourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(Jsons.jsonNode(resetSourceConfiguration))
        .withState(new State()
            .withState(Jsons.jsonNode(createPerStreamState(streamDescriptors))));

    emptyAirbyteSource.start(workerSourceConfig, null);

    streamDescriptors.forEach(streamDescriptor -> {
      Optional<AirbyteMessage> maybeMessage = emptyAirbyteSource.attemptRead();
      Assertions.assertThat(maybeMessage)
          .isNotEmpty();

      AirbyteMessage message = maybeMessage.get();
      Assertions.assertThat(message.getType()).isEqualTo(Type.STATE);

      AirbyteStateMessage stateMessage = message.getState();
      Assertions.assertThat(stateMessage.getStateType()).isEqualTo(AirbyteStateType.STREAM);
      Assertions.assertThat(stateMessage.getStream().getStreamDescriptor()).isEqualTo(streamDescriptor);
      Assertions.assertThat(stateMessage.getStream().getStreamState()).isNull();
    });

    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isEmpty();
  }

  @Test
  public void testPerStreamWithExtraState() throws Exception {
    // This should never happen but nothing keeps us from processing the reset and not fail
    List<StreamDescriptor> streamDescriptors = Lists.newArrayList(
        new StreamDescriptor().withName("a"),
        new StreamDescriptor().withName("b"),
        new StreamDescriptor().withName("c"),
        new StreamDescriptor().withName("d"));

    List<io.airbyte.config.StreamDescriptor> streamToReset = Lists.newArrayList(
        new io.airbyte.config.StreamDescriptor().withName("a"),
        new io.airbyte.config.StreamDescriptor().withName("b"),
        new io.airbyte.config.StreamDescriptor().withName("c"));

    ResetSourceConfiguration resetSourceConfiguration = new ResetSourceConfiguration()
        .withStreamsToReset(streamToReset);
    WorkerSourceConfig workerSourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(Jsons.jsonNode(resetSourceConfiguration))
        .withState(new State()
            .withState(Jsons.jsonNode(createPerStreamState(streamDescriptors))));

    emptyAirbyteSource.start(workerSourceConfig, null);

    streamToReset.forEach(streamDescriptor -> {
      Optional<AirbyteMessage> maybeMessage = emptyAirbyteSource.attemptRead();
      Assertions.assertThat(maybeMessage)
          .isNotEmpty();

      AirbyteMessage message = maybeMessage.get();
      Assertions.assertThat(message.getType()).isEqualTo(Type.STATE);

      AirbyteStateMessage stateMessage = message.getState();
      Assertions.assertThat(stateMessage.getStateType()).isEqualTo(AirbyteStateType.STREAM);
      Assertions.assertThat(stateMessage.getStream().getStreamDescriptor()).isEqualTo(new StreamDescriptor()
          .withName(streamDescriptor.getName())
          .withNamespace(streamDescriptor.getNamespace()));
      Assertions.assertThat(stateMessage.getStream().getStreamState()).isNull();
    });

    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isEmpty();
  }

  private void legacyStateResult() {
    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isNotEmpty()
        .contains(EMPTY_MESSAGE);

    Assertions.assertThat(emptyAirbyteSource.attemptRead())
        .isEmpty();
  }

  private List<AirbyteStateMessage> createPerStreamState(List<StreamDescriptor> streamDescriptors) {
    return streamDescriptors.stream().map(streamDescriptor -> new AirbyteStateMessage()
        .withStateType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState()
                .withStreamDescriptor(streamDescriptor)
                .withStreamState(Jsons.emptyObject())))
        .toList();
  }

  private List<AirbyteStateMessage> createGlobalState(List<StreamDescriptor> streamDescriptors, JsonNode sharedState) {
    AirbyteGlobalState globalState = new AirbyteGlobalState()
        .withSharedState(sharedState)
        .withStreamStates(
            streamDescriptors.stream().map(streamDescriptor -> new AirbyteStreamState()
                .withStreamDescriptor(streamDescriptor)
                .withStreamState(Jsons.emptyObject()))
                .toList());

    return Lists.newArrayList(
        new AirbyteStateMessage()
            .withStateType(AirbyteStateType.GLOBAL)
            .withGlobal(globalState));
  }

}
