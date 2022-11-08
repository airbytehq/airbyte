/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

class StateMessageHelperTest {

  private static final boolean USE_STREAM_CAPABLE_STATE = true;
  private static final boolean DONT_USE_STREAM_CAPABALE_STATE = false;

  @Test
  void testEmpty() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(null, USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isEmpty();
  }

  @Test
  void testEmptyList() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.arrayNode(), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isEmpty();
  }

  @Test
  void testLegacy() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.emptyObject(), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
  }

  @Test
  void testLegacyInList() {
    final JsonNode jsonState = Jsons.jsonNode(List.of(Map.of("Any", "value")));

    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(jsonState, USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
    Assertions.assertThat(stateWrapper.get().getLegacyState()).isEqualTo(jsonState);
  }

  @Test
  void testLegacyInNewFormat() {
    final AirbyteStateMessage stateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.LEGACY)
        .withData(Jsons.emptyObject());
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage)), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
  }

  @Test
  void testGlobal() {
    final AirbyteStateMessage stateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(List.of(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    final Optional<StateWrapper> stateWrapper =
        StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage)), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.GLOBAL);
    Assertions.assertThat(stateWrapper.get().getGlobal()).isEqualTo(stateMessage);
  }

  @Test
  void testGlobalForceLegacy() {
    final JsonNode legacyState = Jsons.jsonNode(1);
    final AirbyteStateMessage stateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(List.of(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))))
        .withData(legacyState);
    final Optional<StateWrapper> stateWrapper =
        StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage)), DONT_USE_STREAM_CAPABALE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
    Assertions.assertThat(stateWrapper.get().getLegacyState()).isEqualTo(legacyState);
  }

  @Test
  void testStream() {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()));
    final Optional<StateWrapper> stateWrapper =
        StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage1, stateMessage2)), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.STREAM);
    Assertions.assertThat(stateWrapper.get().getStateMessages()).containsExactlyInAnyOrder(stateMessage1, stateMessage2);
  }

  @Test
  void testStreamForceLegacy() {
    final JsonNode firstEmittedLegacyState = Jsons.jsonNode(1);
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()))
        .withData(firstEmittedLegacyState);
    final JsonNode secondEmittedLegacyState = Jsons.jsonNode(2);
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))
        .withData(secondEmittedLegacyState);
    final Optional<StateWrapper> stateWrapper =
        StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage1, stateMessage2)), DONT_USE_STREAM_CAPABALE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
    Assertions.assertThat(stateWrapper.get().getLegacyState()).isEqualTo(secondEmittedLegacyState);
  }

  @Test
  void testInvalidMixedState() {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(List.of(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    Assertions
        .assertThatThrownBy(
            () -> StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage1, stateMessage2)), USE_STREAM_CAPABLE_STATE))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  void testDuplicatedGlobalState() {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(List.of(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(List.of(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    Assertions
        .assertThatThrownBy(
            () -> StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage1, stateMessage2)), USE_STREAM_CAPABLE_STATE))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  void testLegacyStateConversion() {
    final StateWrapper stateWrapper = new StateWrapper()
        .withStateType(StateType.LEGACY)
        .withLegacyState(Jsons.deserialize("{\"json\": \"blob\"}"));
    final State expectedState = new State().withState(Jsons.deserialize("{\"json\": \"blob\"}"));

    final State convertedState = StateMessageHelper.getState(stateWrapper);
    Assertions.assertThat(convertedState).isEqualTo(expectedState);
  }

  @Test
  void testGlobalStateConversion() {
    final StateWrapper stateWrapper = new StateWrapper()
        .withStateType(StateType.GLOBAL)
        .withGlobal(
            new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(
                new AirbyteGlobalState()
                    .withSharedState(Jsons.deserialize("\"shared\""))
                    .withStreamStates(Collections.singletonList(
                        new AirbyteStreamState()
                            .withStreamDescriptor(new StreamDescriptor().withNamespace("ns").withName("name"))
                            .withStreamState(Jsons.deserialize("\"stream state\""))))));
    final State expectedState = new State().withState(Jsons.deserialize(
        """
        [{
          "type":"GLOBAL",
          "global":{
             "shared_state":"shared",
             "stream_states":[
               {"stream_descriptor":{"name":"name","namespace":"ns"},"stream_state":"stream state"}
             ]
          }
        }]
        """));

    final State convertedState = StateMessageHelper.getState(stateWrapper);
    Assertions.assertThat(convertedState).isEqualTo(expectedState);
  }

  @Test
  void testStreamStateConversion() {
    final StateWrapper stateWrapper = new StateWrapper()
        .withStateType(StateType.STREAM)
        .withStateMessages(Arrays.asList(
            new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(
                new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withNamespace("ns1").withName("name1"))
                    .withStreamState(Jsons.deserialize("\"state1\""))),
            new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(
                new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withNamespace("ns2").withName("name2"))
                    .withStreamState(Jsons.deserialize("\"state2\"")))));
    final State expectedState = new State().withState(Jsons.deserialize(
        """
        [
          {"type":"STREAM","stream":{"stream_descriptor":{"name":"name1","namespace":"ns1"},"stream_state":"state1"}},
          {"type":"STREAM","stream":{"stream_descriptor":{"name":"name2","namespace":"ns2"},"stream_state":"state2"}}
        ]
        """));

    final State convertedState = StateMessageHelper.getState(stateWrapper);
    Assertions.assertThat(convertedState).isEqualTo(expectedState);
  }

}
