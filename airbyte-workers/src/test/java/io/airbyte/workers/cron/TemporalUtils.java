/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.cron;

import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.filter.v1.WorkflowExecutionFilter;
import io.temporal.api.history.v1.HistoryEvent;
import io.temporal.api.workflowservice.v1.GetWorkflowExecutionHistoryRequest;
import io.temporal.api.workflowservice.v1.GetWorkflowExecutionHistoryResponse;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsResponse;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TemporalUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalUtils.class);

  public static Optional<String> getScheduleIfExists(final WorkflowServiceStubs temporalService, final WorkflowExecution workflowExecution) {
    if (isWorkflowActive(temporalService, workflowExecution)) {
      return Optional.ofNullable(getSchedule(temporalService, workflowExecution));
    } else {
      return Optional.empty();
    }
  }

  public static boolean isWorkflowActive(final WorkflowServiceStubs temporalService, final WorkflowExecution workflowExecution) {
    final ListOpenWorkflowExecutionsResponse listOpenWorkflowExecutionsResponse2 = temporalService.blockingStub()
        .listOpenWorkflowExecutions(ListOpenWorkflowExecutionsRequest.newBuilder()
            .setExecutionFilter(WorkflowExecutionFilter.newBuilder()
                .setWorkflowId(workflowExecution.getWorkflowId()).buildPartial())
            .build());

    return !listOpenWorkflowExecutionsResponse2.getExecutionsList().isEmpty();
  }

  public static String getSchedule(final WorkflowServiceStubs temporalService, final WorkflowExecution workflowExecution) {
    final GetWorkflowExecutionHistoryRequest request =
        GetWorkflowExecutionHistoryRequest.newBuilder()
            .setNamespace("default")
            .setExecution(workflowExecution)
            // .setMaximumPageSize(1)
            .build();
    final GetWorkflowExecutionHistoryResponse result =
        temporalService.blockingStub().getWorkflowExecutionHistory(request);
    final List<HistoryEvent> events = result.getHistory().getEventsList();

    return events.get(0).getWorkflowExecutionStartedEventAttributes().getCronSchedule();
  }

  public static void logSchedule(final WorkflowServiceStubs temporalService, final WorkflowExecution workflowExecution, final int i) {
    LOGGER.info("schedule" + i + " = " + getSchedule(temporalService, workflowExecution));
  }

}
