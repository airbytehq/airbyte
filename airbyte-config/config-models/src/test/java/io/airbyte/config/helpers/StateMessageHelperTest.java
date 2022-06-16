/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

public class StateMessageHelperTest {

  @Test
  public void testEmpty() {
    StateWrapper stateWrapper = StateMessageHelper.getTypedState(null);
    Assertions.assertThat(stateWrapper.getStateType()).isEqualTo(StateType.EMPTY);
  }

  @Test
  public void testLegacy() {
    StateWrapper stateWrapper = StateMessageHelper.getTypedState(Jsons.emptyObject());
    Assertions.assertThat(stateWrapper.getStateType()).isEqualTo(StateType.LEGACY);
  }

  @Test
  public void testGlobal() {
    AirbyteStateMessage stateMessage = new AirbyteStateMessage()
        .withStateType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    StateWrapper stateWrapper = StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage)));
    Assertions.assertThat(stateWrapper.getStateType()).isEqualTo(StateType.GLOBAL);
    Assertions.assertThat(stateWrapper.getGlobal()).isEqualTo(stateMessage);
  }

  @Test
  public void testStream() {
    AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withStateType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()));
    AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withStateType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()));
    StateWrapper stateWrapper = StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage1, stateMessage2)));
    Assertions.assertThat(stateWrapper.getStateType()).isEqualTo(StateType.STREAM);
    Assertions.assertThat(stateWrapper.getStateMessages()).containsExactlyInAnyOrder(stateMessage1, stateMessage2);
  }

  @Test
  public void testInvalidMixedState() {
    AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withStateType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()));
    AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withStateType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    Assertions.assertThatThrownBy(() -> StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage1, stateMessage2))))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  public void testDuplicatedGlobalState() {
    AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withStateType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withStateType(AirbyteStateType.GLOBAL)
        .withGlobal(
            new AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(Lists.newArrayList(
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a")).withStreamState(Jsons.emptyObject()),
                    new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()))));
    Assertions.assertThatThrownBy(() -> StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList(stateMessage1, stateMessage2))))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  public void testEmptyStateList() {
    Assertions.assertThatThrownBy(() -> StateMessageHelper.getTypedState(Jsons.jsonNode(Lists.newArrayList())))
        .isInstanceOf(IllegalStateException.class);
  }

}
