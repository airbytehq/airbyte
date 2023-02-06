/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling.state.listener;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonSubTypes.Type;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import java.util.Queue;
import java.util.UUID;
import lombok.Value;

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME,
              include = JsonTypeInfo.As.PROPERTY,
              property = "type")
@JsonSubTypes({
  @Type(value = TestStateListener.class,
        name = "test"),
  @Type(value = NoopStateListener.class,
        name = "noop")
})
public interface WorkflowStateChangedListener {

  enum StateField {
    CANCELLED,
    DELETED,
    RUNNING,
    SKIPPED_SCHEDULING,
    UPDATED,
    FAILED,
    RESET,
    CONTINUE_AS_RESET,
    SUCCESS,
    CANCELLED_FOR_RESET,
    RESET_WITH_SCHEDULING,
    DONE_WAITING,
    SKIP_SCHEDULING_NEXT_WORKFLOW,
  }

  @Value
  class ChangedStateEvent {

    private final StateField field;
    private final boolean value;

  }

  Queue<ChangedStateEvent> events(UUID testId);

  void addEvent(UUID testId, ChangedStateEvent event);

}
