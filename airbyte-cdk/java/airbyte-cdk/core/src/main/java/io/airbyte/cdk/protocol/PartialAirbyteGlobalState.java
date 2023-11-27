/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.protocol.deser.PartialJsonDeserializer;
import io.airbyte.cdk.protocol.deser.StringIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class PartialAirbyteGlobalState {

  String serializedGlobalState;
  List<PartialAirbyteStreamState> streamStates;

  static PartialAirbyteGlobalState fromJson(final StringIterator message) {
    return PartialJsonDeserializer.parseObject(
        message,
        PartialAirbyteGlobalState::new,
        Map.of(
            "shared_state", (state) -> state.serializedGlobalState = PartialJsonDeserializer.readSerializedValue(message),
            "stream_states", (state) -> state.streamStates =
                PartialJsonDeserializer.readList(message, PartialAirbyteStreamState::fromJson)),
        false);
  }

  @Override
  public String toString() {
    return "PartialAirbyteGlobalState{" +
        "serializedGlobalState='" + serializedGlobalState + '\'' +
        ", streamStates=" + streamStates +
        '}';
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;

    final PartialAirbyteGlobalState that = (PartialAirbyteGlobalState) o;

    if (!Objects.equals(serializedGlobalState, that.serializedGlobalState))
      return false;
    return Objects.equals(streamStates, that.streamStates);
  }

  @Override
  public int hashCode() {
    int result = serializedGlobalState != null ? serializedGlobalState.hashCode() : 0;
    result = 31 * result + (streamStates != null ? streamStates.hashCode() : 0);
    return result;
  }

  public PartialAirbyteGlobalState withSharedState(final JsonNode state) {
    this.serializedGlobalState = Jsons.serialize(state);
    return this;
  }

  public AirbyteGlobalState toFullGlobalState() {
    final AirbyteGlobalState state = new AirbyteGlobalState();
    state.setSharedState(Jsons.deserialize(serializedGlobalState));
    if (streamStates != null) {
      state.setStreamStates(streamStates.stream().map(PartialAirbyteStreamState::toFullStreamState).toList());
    }
    return state;
  }

}
