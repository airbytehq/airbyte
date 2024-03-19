import { useRef } from "react";

import { ConnectorHelper } from "core/domain/connector";
import { ConnectorT } from "core/domain/connector/types";
import { CheckConnectorParams, useCheckConnector } from "hooks/services/useConnector";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import { CheckConnectionRead } from "../../../core/request/AirbyteClient";

export const useTestConnector = (
  props: {
    formType: "source" | "destination";
  } & (
    | { isEditMode: true; isCopyMode?: false; connector: ConnectorT }
    | { isCopyMode: true; isEditMode?: false; connector: ConnectorT }
    | {
        isEditMode?: false;
        isCopyMode?: false;
      }
  )
): {
  isTestConnectionInProgress: boolean;
  isSuccess: boolean;
  onStopTesting: () => void;
  testConnector: (v?: ServiceFormValues) => Promise<CheckConnectionRead>;
  error: Error | null;
  reset: () => void;
} => {
  const { mutateAsync, isLoading, error, isSuccess, reset } = useCheckConnector(props.formType);
  const { workspaceId } = useCurrentWorkspace();

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

      if (props.isEditMode || props.isCopyMode) {
        // When we are editing current connector
        if (values) {
          payload = {
            connectionConfiguration: values.connectionConfiguration,
            name: values.name,
            selectedConnectorId: ConnectorHelper.id(props.connector),
            signal: controller.signal,
            workspaceId,
          };
        } else {
          // just testing current connection
          payload = {
            selectedConnectorId: ConnectorHelper.id(props.connector),
            signal: controller.signal,
            workspaceId,
          };
        }
      } else if (values) {
        // creating new connection
        payload = {
          connectionConfiguration: values.connectionConfiguration,
          signal: controller.signal,
          selectedConnectorDefinitionId: values.serviceType,
          workspaceId,
        };
      }

      if (!payload) {
        throw new Error("Unexpected state met");
      }

      return mutateAsync(payload);
    },
  };
};
