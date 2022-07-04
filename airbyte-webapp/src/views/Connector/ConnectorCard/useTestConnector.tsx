import { useRef } from "react";

import { ConnectorHelper } from "core/domain/connector";
import { ConnectorT } from "core/domain/connector/types";
import { CheckConnectorParams, useCheckConnector } from "hooks/services/useConnector";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import { CheckConnectionRead } from "../../../core/request/AirbyteClient";

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
  testConnector: (v?: ServiceFormValues) => Promise<CheckConnectionRead>;
  error: Error | null;
  reset: () => void;
} => {
  const { mutateAsync, isLoading, error, isSuccess, reset } = useCheckConnector(props.formType);

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
