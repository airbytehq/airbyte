package io.airbyte.workers.temporal.scheduling.state;

import java.util.HashSet;
import java.util.Set;
import lombok.Getter;

@Getter
public class ResetStreamState {
  Set<String> streamBeingReset = new HashSet<>();
  Set<String> streamToReset = new HashSet<>();

  void addStreamToBeProcess(final Set<String> streamNames) {
    streamToReset.addAll(streamNames);
  }

  void failure() {
    streamToReset.addAll(streamBeingReset);
  }

  public void startRunningMethod() {
    streamBeingReset.addAll(streamToReset);
    streamToReset.clear();
  }
}
