import { useCallback, useState } from "react";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import { CheckConnectionRead } from "../../../../core/request/AirbyteClient";
import { useAnalyticsTrackFunctions } from "../useAnalyticsTrackFunctions";

interface UseOnHandleSubmitHookProps {
  setErrorStatusRequest: (error: Error | null) => void;
  availableServices: ConnectorDefinition[];
  formType: "source" | "destination";
  testConnector: (v?: ServiceFormValues) => Promise<CheckConnectionRead>;
  onSubmit: (values: ServiceFormValues) => Promise<void> | void;
}

interface UseOnHandleSubmitHookResult {
  isFormSubmitting: boolean;
  onHandleSubmit: (values: ServiceFormValues) => Promise<void>;
  saved: boolean;
}

export const useOnHandeSubmit = (props: UseOnHandleSubmitHookProps): UseOnHandleSubmitHookResult => {
  const [saved, setSaved] = useState(false);
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const { trackTestConnectorFailure, trackTestConnectorSuccess, trackTestConnectorStarted } =
    useAnalyticsTrackFunctions(props.formType);
  const onHandleSubmit = useCallback(
    async (values: ServiceFormValues) => {
      props.setErrorStatusRequest(null);
      setIsFormSubmitting(true);

      const connector = props.availableServices.find((item) => Connector.id(item) === values.serviceType);

      const testConnectorWithTracking = async () => {
        trackTestConnectorStarted(connector);
        try {
          await props.testConnector(values);
          trackTestConnectorSuccess(connector);
        } catch (e) {
          trackTestConnectorFailure(connector);
          throw e;
        }
      };

      try {
        await testConnectorWithTracking();
        props.onSubmit(values);
        setSaved(true);
      } catch (e) {
        props.setErrorStatusRequest(e);
        setIsFormSubmitting(false);
      }
    },
    [props, trackTestConnectorFailure, trackTestConnectorStarted, trackTestConnectorSuccess]
  );

  return {
    onHandleSubmit,
    isFormSubmitting,
    saved,
  };
};
