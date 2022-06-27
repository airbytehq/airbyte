/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.List;
import java.util.Optional;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

public class StateMessageHelperTest {

  @Test
  public void testEmpty() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(null);
    Assertions.assertThat(stateWrapper).isEmpty();
  }

  @Test
  public void testLegacy() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.emptyObject());
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
  }

  @Test
  public void testLegacyAsList() {
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.emptyObject());
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.LEGACY);
  }

  @Test
  public void testLegacyInNewFormat() {
    final AirbyteStateMessage stateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.LEGACY)
        .withData(Jsons.emptyObject());
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage)));
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
                .withStreamStates(List.of(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage)));
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.GLOBAL);
    Assertions.assertThat(stateWrapper.get().getGlobal()).isEqualTo(stateMessage);
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
    final Optional<StateWrapper> stateWrapper = StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage1, stateMessage2)));
    Assertions.assertThat(stateWrapper).isNotEmpty();
    Assertions.assertThat(stateWrapper.get().getStateType()).isEqualTo(StateType.STREAM);
    Assertions.assertThat(stateWrapper.get().getStateMessages()).containsExactlyInAnyOrder(stateMessage1, stateMessage2);
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
                .withStreamStates(List.of(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    Assertions.assertThatThrownBy(() -> StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage1, stateMessage2))))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  public void testDuplicatedGlobalState() {
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
    Assertions.assertThatThrownBy(() -> StateMessageHelper.getTypedState(Jsons.jsonNode(List.of(stateMessage1, stateMessage2))))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  public void testEmptyStateList() {
    Assertions.assertThatThrownBy(() -> StateMessageHelper.getTypedState(Jsons.jsonNode(List.of())))
        .isInstanceOf(IllegalStateException.class);
  }

}
