/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.Map;
import java.util.Optional;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

public class StateMessageHelperTest {

  private static final boolean USE_STREAM_CAPABLE_STATE = true;
  private static final boolean DONT_USE_STREAM_CAPABALE_STATE = false;

  @Test
  public void testEmpty() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(null, USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isEmpty();
  }

  @Test
  public void testLegacy() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.emptyObject(), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
  }

  @Test
  public void testLegacyInList() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.jsonNode(
        Lists.newArrayList(
            Map.of("Any", "value"))),
        USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
  }

  @Test
  public void testGlobal() {
    final AirbyteStateMessage stateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    final Optional<StateWrapper> stateWrapper =
        StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage)), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.GLOBAL);
    Assertions.assertThat(stateWrapper.get().getGlobal()).isEqualTo(stateMessage);
  }

  @Test
  public void testGlobalForceLegacy() {
    final JsonNode legacyState = Jsons.jsonNode(1);
    final AirbyteStateMessage stateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))))
        .withData(legacyState);
    final Optional<StateWrapper> stateWrapper =
        StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage)), DONT_USE_STREAM_CAPABALE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
    Assertions.assertThat(stateWrapper.get().getLegacyState()).isEqualTo(legacyState);
  }

  @Test
  public void testStream() {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()));
    final Optional<StateWrapper> stateWrapper =
        StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage1, stateMessage2)), USE_STREAM_CAPABLE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.STREAM);
    Assertions.assertThat(stateWrapper.get().getStateMessages()).containsExactlyInAnyOrder(stateMessage1, stateMessage2);
  }

  @Test
  public void testStreamForceLegacy() {
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
        StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage1, stateMessage2)), DONT_USE_STREAM_CAPABALE_STATE);
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
    Assertions.assertThat(stateWrapper.get().getLegacyState()).isEqualTo(secondEmittedLegacyState);
  }

  @Test
  public void testInvalidMixedState() {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    Assertions
        .assertThatThrownBy(
            () -> StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage1, stateMessage2)), USE_STREAM_CAPABLE_STATE))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  public void testDuplicatedGlobalState() {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    Assertions
        .assertThatThrownBy(
            () -> StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage1, stateMessage2)), USE_STREAM_CAPABLE_STATE))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  public void testEmptyStateList() {
    Assertions.assertThatThrownBy(() -> StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList()), USE_STREAM_CAPABLE_STATE))
        .isInstanceOf(IllegalStateException.class);
  }

}
