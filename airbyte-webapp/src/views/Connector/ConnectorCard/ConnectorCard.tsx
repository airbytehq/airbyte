import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { ContentCard } from "components";
import { JobItem } from "components/JobItem/JobItem";

import { Action, Namespace } from "core/analytics";
import { Connector, ConnectorT } from "core/domain/connector";
import { CheckConnectionRead } from "core/request/AirbyteClient";
import { LogsRequestError, SynchronousJobReadWithStatus } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ServiceForm, ServiceFormProps, ServiceFormValues } from "views/Connector/ServiceForm";

import { useTestConnector } from "./useTestConnector";

export interface ConnectorCardProvidedProps {
  isTestConnectionInProgress: boolean;
  isSuccess: boolean;
  onStopTesting: () => void;
  testConnector: (v?: ServiceFormValues) => Promise<CheckConnectionRead>;
}

export const ConnectorCard: React.FC<
  {
    title?: React.ReactNode;
    full?: boolean;
    jobInfo?: SynchronousJobReadWithStatus | null;
  } & Omit<ServiceFormProps, keyof ConnectorCardProvidedProps> &
    (
      | {
          isEditMode: true;
          connector: ConnectorT;
        }
      | { isEditMode?: false }
    )
> = ({ title, full, jobInfo, onSubmit, ...props }) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);

  const { testConnector, isTestConnectionInProgress, onStopTesting, error, reset } = useTestConnector(props);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
    setErrorStatusRequest(null);
  }, [props.selectedConnectorDefinitionSpecification, reset]);

  const analyticsService = useAnalyticsService();

  const onHandleSubmit = async (values: ServiceFormValues) => {
    setErrorStatusRequest(null);

    const connector = props.availableServices.find((item) => Connector.id(item) === values.serviceType);

    const trackAction = (actionType: Action, actionDescription: string) => {
      if (!connector) {
        return;
      }

      const namespace = props.formType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

      analyticsService.track(namespace, actionType, {
        actionDescription,
        connector_source: connector?.name,
        connector_source_definition_id: Connector.id(connector),
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
      await testConnectorWithTracking();
      await onSubmit(values);
      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  return (
    <ContentCard title={title} full={full}>
      <ServiceForm
        {...props}
        errorMessage={props.errorMessage || (error && createFormErrorMessage(error))}
        isTestConnectionInProgress={isTestConnectionInProgress}
        onStopTesting={onStopTesting}
        testConnector={testConnector}
        onSubmit={onHandleSubmit}
        successMessage={
          props.successMessage || (saved && props.isEditMode && <FormattedMessage id="form.changesSaved" />)
        }
      />
      {job && <JobItem job={job} />}
    </ContentCard>
  );
};
