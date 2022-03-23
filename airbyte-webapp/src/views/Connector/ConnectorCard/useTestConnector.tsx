import { useRef } from "react";

import { ServiceFormValues } from "views/Connector/ServiceForm";
import {
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
  Scheduler,
} from "core/domain/connector";
import { useCheckConnector } from "hooks/services/useConnector";

export const useTestConnector = (props: {
  formType: "source" | "destination";
  isEditMode?: boolean;
  selectedConnector?: ConnectorDefinitionSpecification;
}): {
  isTestConnectionInProgress: boolean;
  isSuccess: boolean;
  onStopTesting: () => void;
  testConnector: (v?: ServiceFormValues) => Promise<Scheduler>;
  error: Error | null;
} => {
  const { mutateAsync, isLoading, error, isSuccess, reset } = useCheckConnector(
    props.formType
  );

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

      if (values) {
        if (props.selectedConnector && !props.isEditMode) {
          return mutateAsync({
            connectionConfiguration: values.connectionConfiguration,
            signal: controller.signal,
            selectedConnectorDefinitionId: ConnectorSpecification.id(
              props.selectedConnector
            ),
          });
        } else {
          return mutateAsync({
            connectionConfiguration: values.connectionConfiguration,
            name: values.name,
            selectedConnectorId: "e2152054-cb99-41b8-ae81-f5f45363bb12",
            signal: controller.signal,
          });
        }
      } else {
        return mutateAsync({
          // TODO: FIXME
          selectedConnectorId: "e2152054-cb99-41b8-ae81-f5f45363bb12",
          signal: controller.signal,
        });
      }
    },
  };
};
