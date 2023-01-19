/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import io.airbyte.commons.temporal.exception.DeletedWorkflowException;
import io.airbyte.commons.temporal.exception.UnreachableWorkflowException;
import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.commons.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import io.temporal.api.workflowservice.v1.DescribeWorkflowExecutionRequest;
import io.temporal.api.workflowservice.v1.DescribeWorkflowExecutionResponse;
import io.temporal.client.BatchRequest;
import io.temporal.client.WorkflowClient;
import io.temporal.workflow.Functions.Proc;
import io.temporal.workflow.Functions.Proc1;
import io.temporal.workflow.Functions.TemporalFunctionalInterfaceMarker;
import jakarta.inject.Singleton;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@NoArgsConstructor
@Singleton
@Slf4j
public class ConnectionManagerUtils {

  /**
   * Send a cancellation to the workflow. It will swallow any exception and won't check if the
   * workflow is already deleted when being cancel.
   */
  public void deleteWorkflowIfItExist(final WorkflowClient client,
                                      final UUID connectionId) {
    try {
      final ConnectionManagerWorkflow connectionManagerWorkflow =
          client.newWorkflowStub(ConnectionManagerWorkflow.class, getConnectionManagerName(connectionId));
      connectionManagerWorkflow.deleteConnection();
    } catch (final Exception e) {
      log.warn("The workflow is not reachable when trying to cancel it", e);
    }

  }

  /**
   * Attempts to send a signal to the existing ConnectionManagerWorkflow for the provided connection.
   *
   * If the workflow is unreachable, this will restart the workflow and send the signal in a single
   * batched request. Batching is used to avoid race conditions between starting the workflow and
   * executing the signal.
   *
   * @param client the WorkflowClient for interacting with temporal
   * @param connectionId the connection ID to execute this operation for
   * @param signalMethod a function that takes in a connection manager workflow and executes a signal
   *        method on it, with no arguments
   * @return the healthy connection manager workflow that was signaled
   * @throws DeletedWorkflowException if the connection manager workflow was deleted
   */
  public ConnectionManagerWorkflow signalWorkflowAndRepairIfNecessary(final WorkflowClient client,
                                                                      final UUID connectionId,
                                                                      final Function<ConnectionManagerWorkflow, Proc> signalMethod)
      throws DeletedWorkflowException {
    return signalWorkflowAndRepairIfNecessary(client, connectionId, signalMethod, Optional.empty());
  }

  /**
   * Attempts to send a signal to the existing ConnectionManagerWorkflow for the provided connection.
   *
   * If the workflow is unreachable, this will restart the workflow and send the signal in a single
   * batched request. Batching is used to avoid race conditions between starting the workflow and
   * executing the signal.
   *
   * @param client the WorkflowClient for interacting with temporal
   * @param connectionId the connection ID to execute this operation for
   * @param signalMethod a function that takes in a connection manager workflow and executes a signal
   *        method on it, with 1 argument
   * @param signalArgument the single argument to be input to the signal
   * @return the healthy connection manager workflow that was signaled
   * @throws DeletedWorkflowException if the connection manager workflow was deleted
   */
  public <T> ConnectionManagerWorkflow signalWorkflowAndRepairIfNecessary(final WorkflowClient client,
                                                                          final UUID connectionId,
                                                                          final Function<ConnectionManagerWorkflow, Proc1<T>> signalMethod,
                                                                          final T signalArgument)
      throws DeletedWorkflowException {
    return signalWorkflowAndRepairIfNecessary(client, connectionId, signalMethod, Optional.of(signalArgument));
  }

  // This method unifies the logic of the above two, by using the optional signalArgument parameter to
  // indicate if an argument is being provided to the signal or not.
  // Keeping this private and only exposing the above methods outside this class provides a strict
  // type enforcement for external calls, and means this method can assume consistent type
  // implementations for both cases.
  private <T> ConnectionManagerWorkflow signalWorkflowAndRepairIfNecessary(final WorkflowClient client,
                                                                           final UUID connectionId,
                                                                           final Function<ConnectionManagerWorkflow, ? extends TemporalFunctionalInterfaceMarker> signalMethod,
                                                                           final Optional<T> signalArgument)
      throws DeletedWorkflowException {
    try {
      final ConnectionManagerWorkflow connectionManagerWorkflow = getConnectionManagerWorkflow(client, connectionId);
      log.info("Retrieved existing connection manager workflow for connection {}. Executing signal.", connectionId);
      // retrieve the signal from the lambda
      final TemporalFunctionalInterfaceMarker signal = signalMethod.apply(connectionManagerWorkflow);
      // execute the signal
      if (signalArgument.isPresent()) {
        ((Proc1<T>) signal).apply(signalArgument.get());
      } else {
        ((Proc) signal).apply();
      }
      return connectionManagerWorkflow;
    } catch (final UnreachableWorkflowException e) {
      log.error(
          String.format(
              "Failed to retrieve ConnectionManagerWorkflow for connection %s. Repairing state by creating new workflow and starting with the signal.",
              connectionId),
          e);

      // in case there is an existing workflow in a bad state, attempt to terminate it first before
      // starting a new workflow
      safeTerminateWorkflow(client, connectionId, "Terminating workflow in unreachable state before starting a new workflow for this connection");

      final ConnectionManagerWorkflow connectionManagerWorkflow = newConnectionManagerWorkflowStub(client, connectionId);
      final ConnectionUpdaterInput startWorkflowInput = TemporalWorkflowUtils.buildStartWorkflowInput(connectionId);

      final BatchRequest batchRequest = client.newSignalWithStartRequest();
      batchRequest.add(connectionManagerWorkflow::run, startWorkflowInput);

      // retrieve the signal from the lambda
      final TemporalFunctionalInterfaceMarker signal = signalMethod.apply(connectionManagerWorkflow);
      // add signal to batch request
      if (signalArgument.isPresent()) {
        batchRequest.add((Proc1<T>) signal, signalArgument.get());
      } else {
        batchRequest.add((Proc) signal);
      }

      client.signalWithStart(batchRequest);
      log.info("Connection manager workflow for connection {} has been started and signaled.", connectionId);

      return connectionManagerWorkflow;
    }
  }

  void safeTerminateWorkflow(final WorkflowClient client, final String workflowId, final String reason) {
    log.info("Attempting to terminate existing workflow for workflowId {}.", workflowId);
    try {
      client.newUntypedWorkflowStub(workflowId).terminate(reason);
    } catch (final Exception e) {
      log.warn(
          "Could not terminate temporal workflow due to the following error; "
              + "this may be because there is currently no running workflow for this connection.",
          e);
    }
  }

  public void safeTerminateWorkflow(final WorkflowClient client, final UUID connectionId, final String reason) {
    safeTerminateWorkflow(client, getConnectionManagerName(connectionId), reason);
  }

  public ConnectionManagerWorkflow startConnectionManagerNoSignal(final WorkflowClient client, final UUID connectionId) {
    final ConnectionManagerWorkflow connectionManagerWorkflow = newConnectionManagerWorkflowStub(client, connectionId);
    final ConnectionUpdaterInput input = TemporalWorkflowUtils.buildStartWorkflowInput(connectionId);
    WorkflowClient.start(connectionManagerWorkflow::run, input);

    return connectionManagerWorkflow;
  }

  /**
   * Attempts to retrieve the connection manager workflow for the provided connection.
   *
   * @param connectionId the ID of the connection whose workflow should be retrieved
   * @return the healthy ConnectionManagerWorkflow
   * @throws DeletedWorkflowException if the workflow was deleted, according to the workflow state
   * @throws UnreachableWorkflowException if the workflow is in an unreachable state
   */
  public ConnectionManagerWorkflow getConnectionManagerWorkflow(final WorkflowClient client, final UUID connectionId)
      throws DeletedWorkflowException, UnreachableWorkflowException {

    final ConnectionManagerWorkflow connectionManagerWorkflow;
    final WorkflowState workflowState;
    final WorkflowExecutionStatus workflowExecutionStatus;
    try {
      connectionManagerWorkflow = client.newWorkflowStub(ConnectionManagerWorkflow.class, getConnectionManagerName(connectionId));
      workflowState = connectionManagerWorkflow.getState();
      workflowExecutionStatus = getConnectionManagerWorkflowStatus(client, connectionId);
    } catch (final Exception e) {
      throw new UnreachableWorkflowException(
          String.format("Failed to retrieve ConnectionManagerWorkflow for connection %s due to the following error:", connectionId),
          e);
    }

    if (WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_COMPLETED.equals(workflowExecutionStatus)) {
      if (workflowState.isDeleted()) {
        throw new DeletedWorkflowException(String.format(
            "The connection manager workflow for connection %s is deleted, so no further operations cannot be performed on it.",
            connectionId));
      }

      // A non-deleted workflow being in a COMPLETED state is unexpected, and should be corrected
      throw new UnreachableWorkflowException(
          String.format("ConnectionManagerWorkflow for connection %s is unreachable due to having COMPLETED status.", connectionId));
    }

    return connectionManagerWorkflow;
  }

  Optional<WorkflowState> getWorkflowState(final WorkflowClient client, final UUID connectionId) {
    try {
      final ConnectionManagerWorkflow connectionManagerWorkflow = client.newWorkflowStub(ConnectionManagerWorkflow.class,
          getConnectionManagerName(connectionId));
      return Optional.of(connectionManagerWorkflow.getState());
    } catch (final Exception e) {
      log.error("Exception thrown while checking workflow state for connection id {}", connectionId, e);
      return Optional.empty();
    }
  }

  boolean isWorkflowStateRunning(final WorkflowClient client, final UUID connectionId) {
    return getWorkflowState(client, connectionId).map(WorkflowState::isRunning).orElse(false);
  }

  public WorkflowExecutionStatus getConnectionManagerWorkflowStatus(final WorkflowClient workflowClient, final UUID connectionId) {
    final DescribeWorkflowExecutionRequest describeWorkflowExecutionRequest = DescribeWorkflowExecutionRequest.newBuilder()
        .setExecution(WorkflowExecution.newBuilder()
            .setWorkflowId(getConnectionManagerName(connectionId))
            .build())
        .setNamespace(workflowClient.getOptions().getNamespace()).build();

    final DescribeWorkflowExecutionResponse describeWorkflowExecutionResponse = workflowClient.getWorkflowServiceStubs().blockingStub()
        .describeWorkflowExecution(describeWorkflowExecutionRequest);

    return describeWorkflowExecutionResponse.getWorkflowExecutionInfo().getStatus();
  }

  public long getCurrentJobId(final WorkflowClient client, final UUID connectionId) {
    try {
      final ConnectionManagerWorkflow connectionManagerWorkflow = getConnectionManagerWorkflow(client, connectionId);
      return connectionManagerWorkflow.getJobInformation().getJobId();
    } catch (final Exception e) {
      return ConnectionManagerWorkflow.NON_RUNNING_JOB_ID;
    }
  }

  public ConnectionManagerWorkflow newConnectionManagerWorkflowStub(final WorkflowClient client, final UUID connectionId) {
    return client.newWorkflowStub(ConnectionManagerWorkflow.class,
        TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.CONNECTION_UPDATER, getConnectionManagerName(connectionId)));
  }

  public String getConnectionManagerName(final UUID connectionId) {
    return "connection_manager_" + connectionId;
  }

}
