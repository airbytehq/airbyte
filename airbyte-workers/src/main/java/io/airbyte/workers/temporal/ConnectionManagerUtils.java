/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import io.airbyte.workers.temporal.exception.DeletedWorkflowException;
import io.airbyte.workers.temporal.exception.UnreachableWorkflowException;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.temporal.client.BatchRequest;
import io.temporal.client.WorkflowClient;
import io.temporal.workflow.Functions.Proc;
import io.temporal.workflow.Functions.Proc1;
import io.temporal.workflow.Functions.TemporalFunctionalInterfaceMarker;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import lombok.extern.slf4j.Slf4j;

/**
 * Encapsulates logic specific to retrieving, starting, and signaling the ConnectionManagerWorkflow.
 */
@Slf4j
public class ConnectionManagerUtils {

  /**
   * Attempts to send a signal to the existing ConnectionManagerWorkflow for the provided connection.
   *
   * If the workflow is unreachable, this will restart the workflow and send the signal in a single
   * batched request.
   *
   * @param client the WorkflowClient for interacting with temporal
   * @param connectionId the connection ID to execute this operation for
   * @param signalMethod a function that takes in a connection manager workflow and executes a signal
   *        method on it, with no arguments
   * @return the healthy connection manager workflow that was signaled
   * @throws DeletedWorkflowException if the connection manager workflow was deleted
   */
  static ConnectionManagerWorkflow signalWorkflowAndRepairIfNecessary(final WorkflowClient client,
                                                                      final UUID connectionId,
                                                                      final Function<ConnectionManagerWorkflow, Proc> signalMethod)
      throws DeletedWorkflowException {
    return signalWorkflowAndRepairIfNecessary(client, connectionId, signalMethod, Optional.empty());
  }

  /**
   * Attempts to send a signal to the existing ConnectionManagerWorkflow for the provided connection.
   *
   * If the workflow is unreachable, this will restart the workflow and send the signal in a single
   * batched request.
   *
   * @param client the WorkflowClient for interacting with temporal
   * @param connectionId the connection ID to execute this operation for
   * @param signalMethod a function that takes in a connection manager workflow and executes a signal
   *        method on it, with 1 argument
   * @param signalArgument the single argument to be input to the signal
   * @return the healthy connection manager workflow that was signaled
   * @throws DeletedWorkflowException if the connection manager workflow was deleted
   */
  static <T> ConnectionManagerWorkflow signalWorkflowAndRepairIfNecessary(final WorkflowClient client,
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
  private static <T> ConnectionManagerWorkflow signalWorkflowAndRepairIfNecessary(final WorkflowClient client,
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

      final ConnectionManagerWorkflow connectionManagerWorkflow = newConnectionManagerWorkflowStub(client, connectionId);
      final ConnectionUpdaterInput startWorkflowInput = buildStartWorkflowInput(connectionId);

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

  static ConnectionManagerWorkflow startConnectionManagerNoSignal(final WorkflowClient client, final UUID connectionId) {
    final ConnectionManagerWorkflow connectionManagerWorkflow = newConnectionManagerWorkflowStub(client, connectionId);
    final ConnectionUpdaterInput input = buildStartWorkflowInput(connectionId);

    WorkflowClient.start(connectionManagerWorkflow::run, input);

    return connectionManagerWorkflow;
  }

  /**
   * Attempts to retrieve the connection manager workflow for the provided connection.
   *
   * @param connectionId the ID of the connection whose workflow should be retrieved
   * @return the healthy ConnectionManagerWorkflow
   * @throws DeletedWorkflowException if the workflow was deleted, according to the workflow state
   * @throws UnreachableWorkflowException if the workflow is unreachable
   */
  static ConnectionManagerWorkflow getConnectionManagerWorkflow(final WorkflowClient client, final UUID connectionId)
      throws DeletedWorkflowException, UnreachableWorkflowException {
    final ConnectionManagerWorkflow connectionManagerWorkflow;
    final WorkflowState workflowState;
    try {
      connectionManagerWorkflow = client.newWorkflowStub(ConnectionManagerWorkflow.class, getConnectionManagerName(connectionId));
      workflowState = connectionManagerWorkflow.getState();
    } catch (final Exception e) {
      throw new UnreachableWorkflowException(
          String.format("Failed to retrieve ConnectionManagerWorkflow for connection %s due to the following error:", connectionId),
          e);
    }

    if (workflowState.isDeleted()) {
      throw new DeletedWorkflowException(String.format(
          "The connection manager workflow for connection %s is deleted, so no further operations cannot be performed on it.",
          connectionId));
    }

    return connectionManagerWorkflow;
  }

  static ConnectionManagerWorkflow newConnectionManagerWorkflowStub(final WorkflowClient client, final UUID connectionId) {
    return client.newWorkflowStub(ConnectionManagerWorkflow.class,
        TemporalUtils.getWorkflowOptionsWithWorkflowId(TemporalJobType.CONNECTION_UPDATER, getConnectionManagerName(connectionId)));
  }

  static String getConnectionManagerName(final UUID connectionId) {
    return "connection_manager_" + connectionId;
  }

  static ConnectionUpdaterInput buildStartWorkflowInput(final UUID connectionId) {
    return ConnectionUpdaterInput.builder()
        .connectionId(connectionId)
        .jobId(null)
        .attemptId(null)
        .fromFailure(false)
        .attemptNumber(1)
        .workflowState(null)
        .resetConnection(false)
        .fromJobResetFailure(false)
        .build();
  }

}
