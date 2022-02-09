/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.state;

import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.ChangedStateEvent;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.StateField;
import java.util.UUID;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class WorkflowState {

  public WorkflowState(final UUID id, final WorkflowStateChangedListener stateChangedListener) {
    this.id = id;
    this.stateChangedListener = stateChangedListener;
  }

  private UUID id;
  private WorkflowStateChangedListener stateChangedListener;
  private boolean running = false;
  private boolean deleted = false;
  private boolean skipScheduling = false;
  private boolean updated = false;
  private boolean cancelled = false;
  private boolean failed = false;
  private boolean resetConnection = false;
  private boolean continueAsReset = false;

  public void setRunning(final boolean running) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.RUNNING,
        running);
    stateChangedListener.addEvent(id, event);
    this.running = running;
  }

  public void setDeleted(final boolean deleted) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.DELETED,
        deleted);
    stateChangedListener.addEvent(id, event);
    this.deleted = deleted;
  }

  public void setSkipScheduling(final boolean skipScheduling) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.SKIPPED_SCHEDULING,
        skipScheduling);
    stateChangedListener.addEvent(id, event);
    this.skipScheduling = skipScheduling;
  }

  public void setUpdated(final boolean updated) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.UPDATED,
        updated);
    stateChangedListener.addEvent(id, event);
    this.updated = updated;
  }

  public void setCancelled(final boolean cancelled) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.CANCELLED,
        cancelled);
    stateChangedListener.addEvent(id, event);
    this.cancelled = cancelled;
  }

  public void setFailed(final boolean failed) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.FAILED,
        failed);
    stateChangedListener.addEvent(id, event);
    this.failed = failed;
  }

  public void setResetConnection(final boolean resetConnection) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.RESET,
        resetConnection);
    stateChangedListener.addEvent(id, event);
    this.resetConnection = resetConnection;
  }

  public void setContinueAsReset(final boolean continueAsReset) {
    final ChangedStateEvent event = new ChangedStateEvent(
        StateField.CONTINUE_AS_RESET,
        continueAsReset);
    stateChangedListener.addEvent(id, event);
    this.continueAsReset = continueAsReset;
  }

  public void reset() {
    this.setRunning(false);
    this.setDeleted(false);
    this.setSkipScheduling(false);
    this.setUpdated(false);
    this.setCancelled(false);
    this.setFailed(false);
    this.setResetConnection(false);
    this.setContinueAsReset(false);
  }

}
