package io.airbyte.workers.temporal.scheduling.pojo;

import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow.ResetInput;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

public class TestResetInput {

  @Test
  void testDefaultValue() {
    final ResetInput resetInput = ResetInput.getDefault();

    Assertions.assertThat(resetInput.isGlobal()).isTrue();
    Assertions.assertThat(resetInput.getStreamNames()).isEmpty();
  }

}
