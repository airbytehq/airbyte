import { useRef } from "react";

import { ConnectorHelper } from "core/domain/connector";
import { ConnectorT } from "core/domain/connector/types";
import { CheckConnectionRead } from "core/request/AirbyteClient";
import { CheckConnectorParams, useCheckConnector } from "hooks/services/useConnector";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import { ConnectorCardValues } from "../ConnectorForm";

export const useTestConnector = (
  props: {
    formType: "source" | "destination";
  } & (
    | { isEditMode: true; connector: ConnectorT }
    | {
        isEditMode?: false;
      }
  )
): {
  isTestConnectionInProgress: boolean;
  isSuccess: boolean;
  onStopTesting: () => void;
  testConnector: (v?: ConnectorCardValues) => Promise<CheckConnectionRead>;
  error: Error | null;
  reset: () => void;
} => {
  const { mutateAsync, isLoading, error, isSuccess, reset } = useCheckConnector(props.formType);
  const workspace = useCurrentWorkspace();

  const abortControllerRef = useRef<AbortController | null>(null);

  return {
    isTestConnectionInProgress: isLoading,
    isSuccess,
    error,
    reset,
    onStopTesting: () => {
      abortControllerRef.current?.abort();
      reset();
    },
    testConnector: async (values) => {
      const controller = new AbortController();

      abortControllerRef.current = controller;

      let payload: CheckConnectorParams | null = null;

      if (props.isEditMode) {
        // When we are editing current connector
        if (values) {
          payload = {
            connectionConfiguration: values.connectionConfiguration,
            name: values.name,
            selectedConnectorId: ConnectorHelper.id(props.connector),
            signal: controller.signal,
          };
        } else {
          // just testing current connection
          payload = {
            selectedConnectorId: ConnectorHelper.id(props.connector),
            signal: controller.signal,
          };
        }
      } else if (values) {
        // creating new connection
        payload = {
          connectionConfiguration: values.connectionConfiguration,
          signal: controller.signal,
          selectedConnectorDefinitionId: values.serviceType,
          workspaceId: workspace.workspaceId,
        };
      }

      if (!payload) {
        console.error("Unexpected state met: no connectorId or connectorDefinitionId provided");

        throw new Error("Unexpected state met");
      }

      return mutateAsync(payload);
    },
  };
};
