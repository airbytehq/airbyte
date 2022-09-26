/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import java.util.UUID;
import javax.annotation.Nullable;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.NonNull;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ConnectionUpdaterInput {

  @NonNull
  private UUID connectionId;
  @Nullable
  private Long jobId;
  /**
   * This field is unused, it is kept for compatibility reasons.
   */
  @Nullable
  private Integer attemptId;
  private boolean fromFailure;
  private int attemptNumber;
  /**
   * The state is needed because it has an event listener in it. The event listener only listen to
   * state updates which explains why it is a member of the {@link WorkflowState} class. The event
   * listener is currently (02/18/22) use for testing only.
   */
  @Nullable
  private WorkflowState workflowState;
  private boolean resetConnection;
  @Builder.Default
  private final boolean fromJobResetFailure = false;

  @Builder.Default
  private boolean skipScheduling = false;

}
