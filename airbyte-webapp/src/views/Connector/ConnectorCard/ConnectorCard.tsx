import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Action, Namespace } from "core/analytics";
import { Connector, ConnectorT } from "core/domain/connector";
import { SynchronousJobRead } from "core/request/AirbyteClient";
import { useAnalyticsService } from "hooks/services/Analytics";
import { generateMessageFromError } from "utils/errorStatusMessage";
import { ServiceForm, ServiceFormProps, ServiceFormValues } from "views/Connector/ServiceForm";

import { useTestConnector } from "./useTestConnector";

type ConnectorCardProvidedProps = Omit<
  ServiceFormProps,
  "isKeyConnectionInProgress" | "isSuccess" | "onStopTesting" | "testConnector"
>;

interface ConnectorCardBaseProps extends ConnectorCardProvidedProps {
  title?: React.ReactNode;
  full?: boolean;
  jobInfo?: SynchronousJobRead | null;
  onShowLoading?: (isLoading: boolean, formValues: ServiceFormValues, error: JSX.Element | string | null) => void;
  onBack?: () => void;
  isCopyMode?: boolean;
}

interface ConnectorCardCreateProps extends ConnectorCardBaseProps {
  isEditMode?: false;
}

interface ConnectorCardEditProps extends ConnectorCardBaseProps {
  isEditMode: true;
  connector: ConnectorT;
}

export const ConnectorCard: React.VFC<ConnectorCardCreateProps | ConnectorCardEditProps> = ({
  title,
  full,
  jobInfo,
  onSubmit,
  onShowLoading,
  onBack,
  ...props
}) => {
  const [saved, setSaved] = useState(false);

  const { testConnector, isTestConnectionInProgress, onStopTesting, error, reset } = useTestConnector(props);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
  }, [props.selectedConnectorDefinitionSpecification, reset]);

  const analyticsService = useAnalyticsService();

  const onHandleSubmit = async (values: ServiceFormValues) => {
    if (onShowLoading) {
      onShowLoading(true, values, null);
    }

    const connector = props.availableServices.find((item) => Connector.id(item) === values.serviceType);

    const trackAction = (actionType: Action, actionDescription: string) => {
      if (!connector) {
        return;
      }

      const namespace = props.formType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

      analyticsService.track(namespace, actionType, {
        actionDescription,
        connector: connector?.name,
        connector_definition_id: Connector.id(connector),
      });
    };

    const testConnectorWithTracking = async () => {
      trackAction(Action.TEST, "Test a connector");
      try {
        await testConnector(values);
        trackAction(Action.SUCCESS, "Tested connector - success");
      } catch (e) {
        trackAction(Action.FAILURE, "Tested connector - failure");
        throw e;
      }
    };

    try {
      if (!props.isCopyMode) {
        await testConnectorWithTracking();
      }
      await onSubmit(values);
      setSaved(true);
    } catch (e) {
      if (onShowLoading) {
        const errorMessage = e ? generateMessageFromError(e) : null;
        onShowLoading(false, values, errorMessage);
      }
    }
  };

  return (
    <ServiceForm
      {...props}
      errorMessage={props.errorMessage || (error && generateMessageFromError(error))}
      isTestConnectionInProgress={isTestConnectionInProgress}
      onStopTesting={onStopTesting}
      testConnector={testConnector}
      onSubmit={onHandleSubmit}
      onBack={onBack}
      successMessage={
        props.successMessage || (saved && props.isEditMode && <FormattedMessage id="form.changesSaved" />)
      }
    />
  );
};
