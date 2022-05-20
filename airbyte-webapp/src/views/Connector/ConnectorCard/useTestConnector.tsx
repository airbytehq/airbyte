import { useRef } from "react";

import { ConnectorHelper, Scheduler } from "core/domain/connector";
import { ConnectorT } from "core/domain/connector/types";
import { CheckConnectorParams, useCheckConnector } from "hooks/services/useConnector";
import { ServiceFormValues } from "views/Connector/ServiceForm";

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
  testConnector: (v?: ServiceFormValues) => Promise<Scheduler>;
  error: Error | null;
} => {
  const { mutateAsync, isLoading, error, isSuccess, reset } = useCheckConnector(props.formType);

  const abortControllerRef = useRef<AbortController | null>(null);

  return {
    isTestConnectionInProgress: isLoading,
    isSuccess,
    error,
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
      } else {
        // creating new connection
        if (values) {
          payload = {
            connectionConfiguration: values.connectionConfiguration,
            signal: controller.signal,
            selectedConnectorDefinitionId: values.serviceType,
          };
        }
      }

      if (!payload) {
        console.error("Unexpected state met: no connectorId or connectorDefinitionId provided");

        throw new Error("Unexpected state met");
      }

      return mutateAsync(payload);
    },
  };
};
